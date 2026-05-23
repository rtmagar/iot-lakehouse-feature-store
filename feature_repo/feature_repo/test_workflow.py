from dotenv import load_dotenv; load_dotenv()
from feast import FeatureStore
import pandas as pd
from datetime import datetime

# This guard prevents the script from running when 'feast apply' imports it!
if __name__ == "__main__":
    
    # 1. Connect to your local Feature Store
    store = FeatureStore(repo_path=".")

    # 2. The Data Scientist provides the devices and timestamps they want to train on
    entity_df = pd.DataFrame.from_dict({
        "device_id": ["SENSOR-101", "SENSOR-103", "SENSOR-105"],
        "event_timestamp": [datetime.now(), datetime.now(), datetime.now()]
    })

    # 3. Feast magically fetches the exact correct features from the Iceberg table
    training_data = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "sensor_hourly_stats:avg_temperature_c",
            "sensor_hourly_stats:peak_vibration_hz",
            "sensor_hourly_stats:anomaly_count"
        ]
    ).to_df()

    print("\n--- Features Retrieved for ML Training ---")
    print(training_data)