from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import sys
from datetime import datetime
from nba.nba_etl import NBAProcessor
from football.football_etl import FootballProcessor

def main():
    """
    Main function to orchestrate NBA and Football data processing
    """
    print("=" * 60)
    print("SPORTS ANALYTICS - TEAM STATISTICS EXTRACTION")
    print("=" * 60)
    
    spark = SparkSession.builder \
        .appName("SportsTeamAnalytics") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    spark.conf.set("spark.sql.shuffle.partitions", 50)
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        print("\n🏀 Processing NBA Team Statistics...")
        nba_processor = NBAProcessor(spark)
        nba_stats = nba_processor.process_team_statistics()
        
        print("\n⚽ Processing Football Team Statistics...")
        football_processor = FootballProcessor(spark)
        football_stats = football_processor.process_match_results()
        
        print("\n💾 Saving Results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #saving results in csv format 
                
        # Save to PostgreSQL
        jdbc_url = "jdbc:postgresql://postgres:5432/sparkdb"
        db_properties = {
            "user": "sparkuser",
            "password": "sparkpass",
            "driver": "org.postgresql.Driver"
        }
        nba_stats.write.mode("overwrite").jdbc(jdbc_url, "nba_stats", properties=db_properties)
        football_stats.write.mode("overwrite").jdbc(jdbc_url, "football_stats", properties=db_properties)
        # Optionally, save to a database or other storage as needed
        print("\n✅ Processing completed successfully!")
        print(f"📊 Results saved with timestamp: {timestamp}")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    main()