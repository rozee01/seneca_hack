from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import os

class NBAProcessor:
    def __init__(self, spark):
        self.spark = spark
        self.data_path = "/app/spark-batch-processing/data/nba-player-stats.csv"
    
    def load_nba_data(self):
        """Load NBA game data from CSV"""
        print("📈 Loading NBA game data...")
        
        schema = StructType([
            StructField("gameorder", IntegerType(), True),
            StructField("game_id", StringType(), True),
            StructField("lg_id", StringType(), True),
            StructField("_iscopy", IntegerType(), True),
            StructField("year_id", IntegerType(), True),
            StructField("date_game", StringType(), True),
            StructField("seasongame", IntegerType(), True),
            StructField("is_playoffs", IntegerType(), True),
            StructField("team_id", StringType(), True),
            StructField("fran_id", StringType(), True),
            StructField("pts", IntegerType(), True),
            StructField("elo_i", DoubleType(), True),
            StructField("elo_n", DoubleType(), True),
            StructField("win_equiv", DoubleType(), True),
            StructField("opp_id", StringType(), True),
            StructField("opp_fran", StringType(), True),
            StructField("opp_pts", IntegerType(), True),
            StructField("opp_elo_i", DoubleType(), True),
            StructField("opp_elo_n", DoubleType(), True),
            StructField("game_location", StringType(), True),
            StructField("game_result", StringType(), True),
            StructField("forecast", DoubleType(), True),
            StructField("notes", StringType(), True)
        ])
        
        df = self.spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(self.data_path)
        
        print(f"✅ Loaded {df.count()} NBA game records")
        return df
    
    def calculate_team_statistics(self, df):
        """Calculate comprehensive team statistics"""
        print("🔢 Calculating NBA team statistics...")
        
        # Basic team stats
        team_stats = df.groupBy("team_id", "fran_id", "year_id") \
            .agg(
                count("game_id").alias("games_played"),
                sum(when(col("game_result") == "W", 1).otherwise(0)).alias("wins"),
                sum(when(col("game_result") == "L", 1).otherwise(0)).alias("losses"),
                avg("pts").alias("avg_points_scored"),
                avg("opp_pts").alias("avg_points_conceded"),
                sum("pts").alias("total_points_scored"),
                sum("opp_pts").alias("total_points_conceded"),
                max("pts").alias("highest_score"),
                min("pts").alias("lowest_score"),
                avg("elo_n").alias("avg_elo_rating"),
                sum(when(col("game_location") == "H", 1).otherwise(0)).alias("home_games"),
                sum(when((col("game_location") == "H") & (col("game_result") == "W"), 1).otherwise(0)).alias("home_wins"),
                sum(when(col("game_location") == "A", 1).otherwise(0)).alias("away_games"),
                sum(when((col("game_location") == "A") & (col("game_result") == "W"), 1).otherwise(0)).alias("away_wins"),
                sum(when(col("is_playoffs") == 1, 1).otherwise(0)).alias("playoff_games"),
                sum(when((col("is_playoffs") == 1) & (col("game_result") == "W"), 1).otherwise(0)).alias("playoff_wins")
            )
        
        # Calculate additional metrics
        team_stats = team_stats \
            .withColumn("win_percentage", round((col("wins") / col("games_played")) * 100, 2)) \
            .withColumn("point_differential", round(col("avg_points_scored") - col("avg_points_conceded"), 2)) \
            .withColumn("home_win_percentage", 
                       round(when(col("home_games") > 0, (col("home_wins") / col("home_games")) * 100).otherwise(0), 2)) \
            .withColumn("away_win_percentage", 
                       round(when(col("away_games") > 0, (col("away_wins") / col("away_games")) * 100).otherwise(0), 2)) \
            .withColumn("playoff_win_percentage", 
                       round(when(col("playoff_games") > 0, (col("playoff_wins") / col("playoff_games")) * 100).otherwise(0), 2))
        team_stats = team_stats \
            .withColumn("draws", lit(0)) \
            .withColumn("goals_scored", col("total_points_scored")) \
            .withColumn("goals_conceded", col("total_points_conceded")) \
            .withColumn("season", col("year_id").cast(StringType())) \
            .withColumn("league", lit("NBA")) \
            .withColumn("league_name", lit("NBA")) \
            .withColumn("franchise", col("fran_id")) \
            .withColumn("sport", lit("NBA")) \
            .select(
                "season", "league", "league_name", "team_id", "franchise",
                "games_played", "wins", "losses", "draws",
                "win_percentage", "goals_scored", "goals_conceded",
                "point_differential", "sport"
            )
        return team_stats
    
    def get_season_rankings(self, team_stats):
        """Calculate team rankings within each season"""
        print("🏆 Calculating season rankings...")
        
        window_spec = Window.partitionBy("season").orderBy(desc("win_percentage"))
        
        rankings = team_stats \
            .withColumn("season_rank", row_number().over(window_spec)) \
            .select(
                "season", "league", "league_name", "team_id", "franchise",
                "games_played", "wins", "losses", "draws",
                "win_percentage", "goals_scored", "goals_conceded",
                "point_differential", "sport", "season_rank"
            )
        
        return rankings
    
    def get_historical_performance(self, df):
        """Get historical performance trends"""
        print("📊 Analyzing historical performance...")
        
        historical = df.groupBy("fran_id") \
            .agg(
                countDistinct("year_id").alias("seasons_played"),
                avg("win_equiv").alias("avg_win_equivalent"),
                sum(when(col("game_result") == "W", 1).otherwise(0)).alias("total_wins"),
                sum(when(col("game_result") == "L", 1).otherwise(0)).alias("total_losses"),
                count("game_id").alias("total_games"),
                sum(when(col("is_playoffs") == 1, 1).otherwise(0)).alias("total_playoff_appearances")
            ) \
            .withColumn("overall_win_percentage", 
                       round((col("total_wins") / col("total_games")) * 100, 2))
        
        return historical
    
    def process_team_statistics(self):
        """Main processing function"""
        # Load data
        df = self.load_nba_data()
        
        # Calculate team statistics
        team_stats = self.calculate_team_statistics(df)
        
        # Get rankings
        final_stats = self.get_season_rankings(team_stats)
        
        # Show sample results
        print("\n📋 Sample NBA Team Statistics:")
        final_stats.select("team_id", "franchise", "season", "games_played", "wins", "losses", 
                          "win_percentage", "point_differential", "season_rank") \
                   .orderBy(desc("win_percentage")) \
                   .show(20, truncate=False)
        
        return final_stats