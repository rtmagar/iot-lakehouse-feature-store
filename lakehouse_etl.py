import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, count, when

# 1. Initialize Spark with Iceberg and MinIO (S3) capabilities
print("Initializing PySpark Session and downloading Iceberg/MinIO drivers...")

spark = SparkSession.builder \
    .appName("IoT-Feature-Engineering") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.lakehouse.type", "hadoop") \
    .config("spark.sql.catalog.lakehouse.warehouse", "s3a://warehouse/") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

# Hide excessive Spark logs for a cleaner terminal
spark.sparkContext.setLogLevel("WARN")

# 2. Read Raw Telemetry Data
print("Reading raw IoT telemetry from MinIO 'raw-telemetry' bucket...")
raw_df = spark.read.json("s3a://raw-telemetry/*/*/*/*/*.json")

print("\n--- Raw Data Schema ---")
raw_df.printSchema()

# 3. Transform & Engineer ML Features
print("Aggregating data into ML features per device...")
feature_df = raw_df.groupBy("device_id").agg(
    avg("temperature_c").alias("avg_temperature_c"),
    max("vibration_hz").alias("peak_vibration_hz"),
    count(when(col("status") == "WARNING", True)).alias("anomaly_count")
)

print("\n--- Processed Feature Data ---")
feature_df.show()

# 4. Write to Apache Iceberg
print("Writing features to Apache Iceberg table in MinIO 'warehouse' bucket...")

# Create the 'iot' namespace (database) if it doesn't exist yet
spark.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.iot")

# Use saveAsTable to register it in the Iceberg catalog properly
feature_df.write \
    .format("iceberg") \
    .mode("overwrite") \
    .saveAsTable("lakehouse.iot.sensor_features")

print("ETL Job Complete! Data successfully committed to the Lakehouse.")
spark.stop()