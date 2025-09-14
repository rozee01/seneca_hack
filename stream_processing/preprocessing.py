from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, trim, from_json, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from transformers import pipeline
import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
mongo_uri = "mongodb://mongouser:mongopass@mongodb:27017/sportpulse_db?authSource=admin"

# -------------------------------
# 1️⃣ Initialize Spark
# -------------------------------
os.environ["HF_HOME"] = "/tmp/huggingface"

spark = (
    SparkSession.builder
    .appName("TweetPreprocessingWithSentiment")
    .master("local[1]")  # Single worker
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:/dev/null")
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:/dev/null")
    .config("spark.logConf", "false")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")
print("[DEBUG] Spark session started.")

# -------------------------------
# 2️⃣ Read from Kafka
# -------------------------------
raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribePattern", ".*")
    .option("startingOffsets", "latest")
    .load()
)

print("[DEBUG] Kafka stream initialized.")

tweets_df = raw_df.selectExpr("CAST(value AS STRING) as json_str", "topic")
tweets_df = tweets_df.filter(~col("topic").contains("cleaned"))

# -------------------------------
# 3️⃣ Define JSON schema
# -------------------------------
schema = StructType([
    StructField("file_name", StringType()),
    StructField("location", StringType()),
    StructField("screenname", StringType()),
    StructField("search_query", StringType()),
    StructField("text", StringType()),
    StructField("retweet_count", StringType()),
])

df = tweets_df.select(from_json(col("json_str"), schema).alias("data"), col("topic")) \
              .select("data.*", "topic")

# -------------------------------
# 4️⃣ Text cleaning
# -------------------------------
df_clean = (
    df.withColumn("clean_text", lower(col("text")))
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"http\S+", ""))   # URLs
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"@\w+", ""))      # mentions
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"#", ""))         # hashtags
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"[^a-zA-Z0-9\s]", ""))  # special chars
      .withColumn("clean_text", trim(col("clean_text")))
)


# -------------------------------
# 5️⃣ Global model singleton
# -------------------------------
_model = None

def get_model():
    global _model
    if _model is None:
        print("[DEBUG] Loading HuggingFace model inside executor...")
        _model = pipeline(
            "sentiment-analysis",
            model="cointegrated/rubert-tiny-sentiment-balanced"
        )
    return _model

# -------------------------------
# 6️⃣ Process each micro-batch
# -------------------------------
def process_batch(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        print(f"[DEBUG] Batch {batch_id}: Empty batch.")
        return

    model = get_model()
    pdf = batch_df.toPandas()
    
    # Run sentiment analysis
    results = model(pdf["clean_text"].tolist(), truncation=False)
    pdf["sentiment_label"] = [r["label"] for r in results]
    pdf["sentiment_score"] = [float(r["score"]) for r in results]

    # Convert back to Spark DataFrame
    spark_df = spark.createDataFrame(pdf)

    # Write to Kafka per topic
    for row in spark_df.select("topic").distinct().collect():
        team = row["topic"]
        cleaned_topic = f"cleaned_{team.replace(' ', '_')}"
        team_df = spark_df.filter(col("topic") == team)
        team_df.selectExpr(
            "CAST(topic AS STRING) AS key",
            "to_json(struct(*)) AS value"
        ).write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("topic", cleaned_topic) \
        .mode("append") \
        .save()

        # -------------------------------
    # MongoDB Save (commented)
    # -------------------------------

    try:
        mongo_client = MongoClient(mongo_uri)
        db = mongo_client['sportpulse_db']
        collection = db.cleaned_tweets
        batch_data = pdf.to_dict(orient="records")
        for doc in batch_data:
            doc["processed_at"] = datetime.utcnow()
            doc["batch_id"] = batch_id
        if batch_data:
            result = collection.insert_many(batch_data)
            print(f"[DEBUG] Inserted {len(result.inserted_ids)} documents into MongoDB.")
        mongo_client.close()
    except Exception as e:
        print(f"[ERROR] Error saving to MongoDB: {e}")

# -------------------------------
# 7️⃣ Start streaming
# -------------------------------
query = df_clean.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "/tmp/spark_checkpoint_tweets_sentiment") \
    .trigger(processingTime='1 second') \
    .start()

query.awaitTermination()
