from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, trim

# 1. Initialiser Spark
spark = SparkSession.builder.appName("TweetPreprocessing").getOrCreate()

# 2. Charger dataset
df = spark.read.csv("NBADataset.csv", header=True, inferSchema=True)

# 3. Garder seulement colonnes utiles
df = df.select("created_at", "screenname", "followers", "friends", 
               "retweet_count", "location", "search_query", "text")

# 4. Nettoyage du texte
df_clean = (
    df.withColumn("clean_text", lower(col("text")))  # minuscule
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"http\S+", ""))  # URLs
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"@\w+", ""))    # mentions
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"#", ""))       # supprimer le #
      .withColumn("clean_text", regexp_replace(col("clean_text"), r"[^a-zA-Z0-9\s]", "")) # caractères spéciaux
      .withColumn("clean_text", trim(col("clean_text")))  # enlever espaces début/fin
)

# 5. Voir un aperçu
df_clean.select("text", "clean_text").show(10, truncate=False)
