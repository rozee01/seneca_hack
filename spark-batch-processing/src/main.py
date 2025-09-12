from pyspark.sql import SparkSession
from nba.nba_etl import run_nba_etl
from football.football_etl import run_football_etl

def main():
    spark = SparkSession.builder \
        .appName("Sports Data ETL") \
        .getOrCreate()

    run_nba_etl(spark)
    run_football_etl(spark)

    spark.stop()

if __name__ == "__main__":
    main()