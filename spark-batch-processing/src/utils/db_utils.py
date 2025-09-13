from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
import psycopg2
from psycopg2 import sql
import os

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def execute_query(query: str, params: tuple = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
        conn.close()

def load_dataframe_to_postgres(df: DataFrame, table_name: str):
    conn = get_db_connection()
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}") \
        .option("dbtable", table_name) \
        .option("user", os.getenv('DB_USER')) \
        .option("password", os.getenv('DB_PASSWORD')) \
        .mode("append") \
        .save()