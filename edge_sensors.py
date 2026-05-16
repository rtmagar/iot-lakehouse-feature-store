import boto3
import json
import time
import random
import uuid
from datetime import datetime, timezone

# Configure boto3 to point to our local MinIO container
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='password123',
    region_name='us-east-1'
)

BUCKET_NAME = 'raw-telemetry'

def generate_sensor_data():
    """Simulates realistic telemetry from manufacturing equipment."""
    device_id = f"SENSOR-{random.randint(100, 105)}"
    
    # Simulate normal ranges with occasional anomalies
    is_anomaly = random.random() > 0.95
    temperature = random.uniform(85.0, 105.0) if not is_anomaly else random.uniform(110.0, 130.0)
    vibration = random.uniform(0.1, 0.5) if not is_anomaly else random.uniform(0.8, 1.5)

    payload = {
        "event_id": str(uuid.uuid4()),
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(temperature, 2),
        "vibration_hz": round(vibration, 2),
        "status": "WARNING" if is_anomaly else "OK"
    }
    return payload

print(f"Starting IoT Sensor Stream to MinIO bucket '{BUCKET_NAME}'... Press Ctrl+C to stop.")

try:
    while True:
        # Generate the mock data
        data = generate_sensor_data()
        
        # Create a unique file path partitioned by date and hour
        now = datetime.now(timezone.utc)
        file_key = f"year={now.year}/month={now.month:02d}/day={now.day:02d}/hour={now.hour:02d}/{data['event_id']}.json"
        
        # Push to MinIO (Local S3)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
        print(f"[{data['timestamp']}] Pushed data for {data['device_id']} -> {file_key}")
        
        # Stream one record every 2 seconds
        time.sleep(2)

except KeyboardInterrupt:
    print("\nSensor stream stopped by user.")