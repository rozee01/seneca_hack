from pyspark.sql import SparkSession
import os
import json
from utils.db_utils import connect_to_db, execute_query

def read_football_data(spark, json_folder_path):
    json_files = []
    for root, _, files in os.walk(json_folder_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    return spark.read.json(json_files)

def transform_football_data(df):
    transformed_df = df.select("date", "home_team", "away_team", "score").withColumnRenamed("home_team", "home") \
        .withColumnRenamed("away_team", "away").withColumnRenamed("score", "match_score")
    return transformed_df

def load_to_postgres(df, table_name):
    db_connection = connect_to_db()
    df.write \
        .format("jdbc") \
        .option("url", db_connection['url']) \
        .option("dbtable", table_name) \
        .option("user", db_connection['user']) \
        .option("password", db_connection['password']) \
        .mode("append") \
        .save()

def main():
    spark = SparkSession.builder \
        .appName("Football ETL") \
        .getOrCreate()

    json_folder_path = "data/football.json"
    football_df = read_football_data(spark, json_folder_path)
    transformed_football_df = transform_football_data(football_df)
    load_to_postgres(transformed_football_df, "football_matches")

    spark.stop()

if __name__ == "__main__":
    main()