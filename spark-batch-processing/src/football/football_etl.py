from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import os
import glob

class FootballProcessor:
    def __init__(self, spark):
        self.spark = spark
        self.data_path = os.path.join(os.getcwd(), "/app/spark-batch-processing/data/football.json")
    
    def load_football_data(self):
        """Load all football JSON data"""
        print("📈 Loading Football match data...")
        
        # Get all JSON files
        json_files = []
        for root, dirs, files in os.walk(self.data_path):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.normpath(os.path.join(root, file)))
        
        print(f"Found {len(json_files)} football data files")
        
        all_matches = []
        
        for file_path in json_files:
            try:
                path_parts = os.path.normpath(file_path).split(os.sep)
                season = path_parts[-2]
                league_file = path_parts[-1]
                league_code = league_file.replace('.json', '')
                df = self.spark.read.json(file_path,multiLine = True)   
                df = df.repartition(16)
                if 'matches' in df.columns:
                    matches_df = df.select(
                        lit(season).alias("season"),
                        lit(league_code).alias("league"),
                        col("name").alias("league_name"),
                        explode("matches").alias("match")
                    ).select(
                        "season", "league", "league_name",
                        col("match.round").alias("round"),
                        col("match.date").alias("date"),
                        col("match.time").alias("time"),
                        col("match.team1").alias("team1"),
                        col("match.team2").alias("team2"),
                        when(
                            col("match.score").isNotNull() & 
                            col("match.score.ft").isNotNull() & 
                            (size(col("match.score.ft")) == 2),
                            col("match.score.ft")
                        ).otherwise(None).alias("final_score")
                    ).filter(
                        col("final_score").isNotNull()
                    )
                                        
                    all_matches.append(matches_df)
                    
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        if all_matches:
            combined_df = all_matches[0]
            for df in all_matches[1:]:
                combined_df = combined_df.union(df)
            
            print(f"✅ Loaded {combined_df.count()} football matches")
            return combined_df
        else:
            print("❌ No football data loaded")
            return self.spark.createDataFrame([], StructType([]))
        
    def process_match_results(self):
        """Process match results to get team statistics"""
        print("🔢 Processing football match results...")

        df = self.load_football_data()
        print("Data matches loaded into a dataframe ")
        # Extract scores from the final_score array
        matches_processed = df \
            .withColumn("team1_goals", col("final_score")[0]) \
            .withColumn("team2_goals", col("final_score")[1]) \
            .filter((col("team1_goals").isNotNull()) & (col("team2_goals").isNotNull()))
        team1_stats = matches_processed.select(
            col("season"),
            col("league"),
            col("league_name"),
            col("team1").alias("team"),
            col("team2").alias("opponent"),
            col("team1_goals").alias("goals_scored"),
            col("team2_goals").alias("goals_conceded"),
            when(col("team1_goals") > col("team2_goals"), "win")
                .when(col("team1_goals") < col("team2_goals"), "loss")
                .otherwise("draw").alias("result")
        )
        team2_stats = matches_processed.select(
            col("season"),
            col("league"),
            col("league_name"),
            col("team2").alias("team"),
            col("team1").alias("opponent"),
            col("team2_goals").alias("goals_scored"),
            col("team1_goals").alias("goals_conceded"),
            when(col("team2_goals") > col("team1_goals"), "win")
                .when(col("team2_goals") < col("team1_goals"), "loss")
                .otherwise("draw").alias("result")
        )

        all_stats = team1_stats.union(team2_stats)
        agg_stats = all_stats.groupBy("season", "league", "league_name", "team") \
            .agg(
                count("*").alias("games_played"),
                sum(when(col("result") == "win", 1).otherwise(0)).alias("wins"),
                sum(when(col("result") == "draw", 1).otherwise(0)).alias("draws"),
                sum(when(col("result") == "loss", 1).otherwise(0)).alias("losses"),
                sum(col("goals_scored")).alias("goals_scored"),
                sum(col("goals_conceded")).alias("goals_conceded")
            )
        window_spec = Window.partitionBy("season", "league", "league_name").orderBy(col("wins").desc(), col("win_percentage").desc())

        agg_stats = agg_stats \
            .withColumn("win_percentage", round((col("wins") / col("games_played")) * 100, 2)) \
            .withColumn("point_differential", col("goals_scored") - col("goals_conceded")) \
            .withColumn("season_rank", rank().over(window_spec)) \
            .withColumn("franchise", col("team")) \
            .withColumn("sport", lit("Football")) \
            .select(
                "season", "league", "league_name", "team", "franchise",
                "games_played", "wins", "losses", "draws",
                "win_percentage", "goals_scored", "goals_conceded",
                "point_differential", "season_rank", "sport"
            ) \
            .orderBy("season", "league", "team")

        print("✅ Team statistics processed")
        print("\n📋 Sample Football Team Statistics:")
        agg_stats.show(5)

        return agg_stats

