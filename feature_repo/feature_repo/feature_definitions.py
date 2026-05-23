from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int64

# 1. Define the Data Source
# We append /data/ so Feast reads the Parquet files directly, ignoring Iceberg metadata
sensor_source = FileSource(
    name="sensor_data_source",
    path="s3://warehouse/iot/sensor_features/data/",
    timestamp_field="event_timestamp", 
)

# 2. Define the Entity
# Using the correct ValueType enum to satisfy typeguard
device = Entity(
    name="device",
    join_keys=["device_id"],
    value_type=ValueType.STRING
)

# 3. Define the Feature View
sensor_hourly_stats_view = FeatureView(
    name="sensor_hourly_stats",
    entities=[device],
    ttl=timedelta(days=1), 
    schema=[
        Field(name="avg_temperature_c", dtype=Float32),
        Field(name="peak_vibration_hz", dtype=Float32),
        Field(name="anomaly_count", dtype=Int64),
    ],
    source=sensor_source,
)