from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd
from utils.db_utils import get_db_connection

def read_nba_data(file_path):
    return pd.read_csv(file_path)

def transform_nba_data(df):
    # Example transformation: Select relevant columns and rename them
    transformed_df = df.select(
        col("Player").alias("player_name"),
        col("Team").alias("team"),
        col("Points").alias("points"),
        col("Assists").alias("assists"),
        col("Rebounds").alias("rebounds")
    )
    return transformed_df

def load_nba_data_to_postgres(df, table_name):
    conn = get_db_connection()
    df.write \
        .format("jdbc") \
        .option("url", conn['url']) \
        .option("dbtable", table_name) \
        .option("user", conn['user']) \
        .option("password", conn['password']) \
        .mode("append") \
        .save()

def main():
    spark = SparkSession.builder \
        .appName("NBA ETL Process") \
        .getOrCreate()

    nba_data_path = "data/nba-player-stats.csv"
    nba_df = read_nba_data(nba_data_path)
    transformed_nba_df = transform_nba_data(nba_df)
    load_nba_data_to_postgres(transformed_nba_df, "nba_stats")

if __name__ == "__main__":
    main()