# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


# COMMAND ----------

# Initialize Spark session
spark = SparkSession \
    .builder \
    .appName("KafkaStream") \
    .getOrCreate()

# Define the schema of the call data
schema = StructType([
    StructField("call_id", StringType(), True),
    StructField("call_start_time", StringType(), True),
    StructField("call_end_time", StringType(), True),
    StructField("caller_id", StringType(), True),
    StructField("agen_not", StringType(), True),
    StructField("transcript", StringType(), True)
])

# Read data from Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "<kafka_broker>:<port>") \
    .option("subscribe", "<topic_name>") \
    .option("startingOffsets", "latest") \
    .load()

 
# Convert the binary value column to string
kafka_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Parse the JSON data and apply the schema
parsed_df = kafka_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Write the streaming data to a Delta table
query = parsed_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/path/to/checkpoint/dir") \
    .option("path", "/path/to/delta/table") \
    .start()

# Wait for the streaming query to finish
query.awaitTermination()

