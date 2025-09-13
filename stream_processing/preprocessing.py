from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, trim, from_json
from pyspark.sql.types import StructType, StructField, StringType
from pymongo import MongoClient
from datetime import datetime
import os
import json

# -------------------------------
# 1️⃣ Initialize Spark
# -------------------------------
import os
os.environ["PYSPARK_SUBMIT_ARGS"] = """
--conf spark.driver.extraJavaOptions='-Dlog4j.configuration=file:/dev/null' 
--conf spark.executor.extraJavaOptions='-Dlog4j.configuration=file:/dev/null' 
pyspark-shell
"""

# -------------------------------
# 2️⃣ Initialize Spark with minimal logging
# -------------------------------
spark = (
    SparkSession.builder
    .appName("TweetPreprocessingDebug")
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:/dev/null")
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:/dev/null")
    .config("spark.logConf", "false")
    .getOrCreate()
)

# Set log level to OFF
spark.sparkContext.setLogLevel("OFF")

print("[DEBUG] Spark session started with logging disabled.")

# -------------------------------
# 2.5️⃣ Initialize MongoDB connection
# -------------------------------

# MongoDB connection string
mongo_uri = f"mongodb://mongouser:mongopass@mongodb:27017/sportpulse_db?authSource=admin"

print(f"[DEBUG] MongoDB URI configured: mongodb://mongouser:***@mongodb:27017/sportpulse_db")

def get_mongo_client():
    """Get MongoDB client connection"""
    try:
        client = MongoClient(mongo_uri)
        # Test the connection
        client.admin.command('ping')
        print("[DEBUG] MongoDB connection successful.")
        return client
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        return None

# -------------------------------
# 2️⃣ Read from Kafka (all team topics)
# -------------------------------
raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")  # use the Docker service name & internal port
    .option("subscribePattern", ".*")
    .option("startingOffsets", "latest")
    .load()
)


print("[DEBUG] Kafka stream initialized.")

# Cast value to string and keep original topic
tweets_df = raw_df.selectExpr(
    "CAST(value AS STRING) as json_str",
    "topic"
)
# Filter out topics that contain 'cleaned'
tweets_df = tweets_df.filter(~col("topic").contains("cleaned"))

# -------------------------------
# 3️⃣ Define schema for JSON messages
# -------------------------------
schema = StructType([
    StructField("file_name", StringType()),
    StructField("location", StringType()),
    StructField("screenname", StringType()),
    StructField("search_query", StringType()),
    StructField("text", StringType()),
])

df = tweets_df.select(
    from_json(col("json_str"), schema).alias("data"),
    col("topic")
).select("data.*", "topic")

print("[DEBUG] Schema applied and JSON parsed.")

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
print("[DEBUG] Text cleaning applied.")

# -------------------------------
# 5️⃣ Function to save to MongoDB and Kafka
# -------------------------------
def save_to_mongodb_and_kafka(batch_df, batch_id):
    if batch_df.count() == 0:
        print(f"[DEBUG] Batch {batch_id}: Empty batch.")
        return

    print(f"[DEBUG] Processing batch {batch_id} with {batch_df.count()} records.")
    
    # Get MongoDB client
    mongo_client = get_mongo_client()
    if mongo_client is None:
        print("[ERROR] Could not connect to MongoDB. Skipping MongoDB save.")
        return
    
    try:
        db = mongo_client['sportpulse_db']
        collection = db.cleaned_tweets
        
        # Convert Spark DataFrame to list of dictionaries for MongoDB
        batch_data = []
        for row in batch_df.collect():
            document = {
                "file_name": row.file_name,
                "location": row.location,
                "screenname": row.screenname,
                "search_query": row.search_query,
                "original_text": row.text,
                "clean_text": row.clean_text,
                "topic": row.topic,
                "processed_at": datetime.utcnow(),
                "batch_id": batch_id
            }
            batch_data.append(document)
        
        # Insert into MongoDB
        if batch_data:
            result = collection.insert_many(batch_data)
            print(f"[DEBUG] Inserted {len(result.inserted_ids)} documents into MongoDB.")
        
        # Also save to Kafka topics (keeping original functionality)
        teams = [row['topic'] for row in batch_df.select("topic").distinct().collect()]
        for team in teams:
            team_df = batch_df.filter(col("topic") == team)
            cleaned_topic = f"cleaned_{team.replace(' ', '_')}"
            print(f"[DEBUG] Writing {team_df.count()} rows to Kafka topic '{cleaned_topic}'")
            team_df.selectExpr(
                "CAST(topic AS STRING) as key",
                "to_json(struct(*)) AS value"
            ).write \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:29092") \
            .option("topic", cleaned_topic) \
            .mode("append") \
            .save()
            
    except Exception as e:
        print(f"[ERROR] Error saving to MongoDB: {e}")
    finally:
        if mongo_client:
            mongo_client.close()

# -------------------------------
# 6️⃣ Start streaming
# -------------------------------
query = df_clean.writeStream \
    .foreachBatch(save_to_mongodb_and_kafka) \
    .option("checkpointLocation", "/tmp/spark_checkpoint_tweets_debug") \
    .trigger(processingTime='1 second') \
    .start()

print("[DEBUG] Streaming query started.")
query.awaitTermination()
