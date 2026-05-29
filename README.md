# IoT Modern Lakehouse & ML Feature Store

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-Infrastructure-2496ED?style=flat&logo=docker&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-Local_Object_Storage-C7202C?style=flat&logo=minio&logoColor=white)
![Apache Spark](https://img.shields.io/badge/PySpark-Lakehouse_ETL-E25A1C?style=flat&logo=apachespark&logoColor=white)
![Apache Iceberg](https://img.shields.io/badge/Apache_Iceberg-ACID_Table_Format-0081C9?style=flat&logo=apache&logoColor=white)
![Feast](https://img.shields.io/badge/Feast-ML_Feature_Store-32D296?style=flat)

## Project Overview
This project simulates a manufacturing company managing thousands of IoT sensors generating massive volumes of telemetry data every hour. The goal was to build a cost-effective, highly reliable process to store raw data and refine it into AI-ready features. 

Instead of relying on managed cloud services, this project is a **100% local, zero-cost architecture**. It demonstrates a deep, low-level understanding of how distributed tools (Spark, Iceberg, Feature Stores) connect and configure manually.

## Tech Stack
* **Storage Layer:** MinIO (Local S3-compatible Object Storage) 
* **Compute Engine:** Apache Spark / PySpark 3.5.1 (Official Apache Docker Image) 
* **Table Format:** Apache Iceberg (providing ACID transactions and Time Travel) 
* **MLOps Feature Store:** Feast (Open-Source feature registry and serving) 
* **Infrastructure:** Docker & Docker-Compose 
* **Languages & Libraries:** Python, `boto3`, `pandas`, `dask`, `s3fs` 

## Architecture Flow
```mermaid
graph TD
    %% Define Styles
    classDef edge fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#fbc02d,stroke-width:2px
    classDef compute fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef mlops fill:#f3e5f5,stroke:#4caf50,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#8e24aa,stroke-width:2px

    %% Nodes
    Edge["The Edge (Simulated)<br><code>edge_sensors.py</code>"]:::edge
    RawStorage["Raw Data Lake (MinIO)<br><code>raw-telemetry</code> Bucket"]:::storage
    Airflow{"Apache Airflow<br>Workflow Orchestration"}:::compute
    Spark["Apache Spark (PySpark)<br><code>lakehouse_etl.py</code>"]:::compute
    Iceberg["Lakehouse (Apache Iceberg)<br><code>warehouse</code> Bucket (MinIO)"]:::storage
    Feast["Feast Feature Store<br><code>feature_definitions.py</code>"]:::mlops
    ML["ML Model Training<br><code>test_workflow.py</code>"]:::output

    %% Connections
    Edge -->|Streams Real-Time Data| RawStorage
    Airflow -->|Triggers ETL Job| Spark
    RawStorage -->|Reads Raw Telemetry| Spark
    Spark -->|Writes ACID-Compliant Upserts| Iceberg
    Iceberg -->|Reads Parquet Files| Feast
    Feast -->|Serves Point-in-Time Features| ML
```
## Core Engineering Challenges Overcome
* **Iceberg Time Travel & Schema Evolution:** Navigated Iceberg's metadata versioning and resolved `KeyError` schema mismatches during point-in-time feature extraction by managing Iceberg's snapshot retention. Guaranteed "Point-in-Time Correctness" for ML models by ensuring all feature writes included an `event_timestamp`.
* **Zero-Cost Local Infrastructure:** Bypassed deprecated vendor Docker registries (Bitnami) by configuring the official `apache/spark:3.5.1` images directly, ensuring native multi-architecture support (Apple Silicon compatibility).
* **Complex S3 Routing for MLOps:** Successfully rerouted Feast's underlying AWS SDK (`boto3`/`pyarrow`) to target the local MinIO container instead of Amazon Cloud servers by configuring environment variables (`.env`) and installing the `s3fs` adapter for Dask/Pandas.

## How to Run Locally

**1. Clone and Set Up the Environment**
```bash
# Clone the repo
git clone https://github.com/rtmagar/iot-lakehouse-feature-store.git
cd iot-lakehouse-feature-store

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install the required Python packages
pip install pyspark feast pandas boto3 s3fs python-dotenv
```
**2. Start the Infrastructure**: Spin up the local MinIO (Storage) and Apache Spark (Compute) containers in the background.
```bash
docker-compose up -d
```
 __Verify MinIO__: *Open your browser to http://localhost:9001 (Username: admin, Password: password123) to view the raw and warehouse buckets.*

__Verify Spark__: *Open http://localhost:8080 to see the Spark Master UI.*


**3. Configure Environment Variables**: To ensure the Python scripts and Feast can communicate with the local MinIO container instead of real AWS servers, configure your environment variables. 
Navigate to the Feast directory and create a ```.env``` file:
```bash
cd feature_repo/feature_repo
touch .env
```
*Add the following exactly as written to your new ```.env``` file:*
```bash
export AWS_ACCESS_KEY_ID=admin
export AWS_SECRET_ACCESS_KEY=password123
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:9000
export S3_ENDPOINT_URL=http://localhost:9000
```
**Note:** *Run ```source .env``` in your terminal to load these variables before proceeding.*

**4. Generate Mock IoT Telemetry (The Edge)**: Navigate back to the project root and start the edge device simulation. This script streams continuous JSON telemetry data (temperature, vibration) directly into the MinIO raw-telemetry bucket.
```bash
cd ../..
python edge_sensors.py
```

**5. Run the PySpark ETL Job**: Process the raw JSON data into an ACID-compliant Apache Iceberg table. This script aggregates the metrics, flags anomalies, adds a point-in-time timestamp, and saves it to the ```warehouse``` bucket.
```bash
python lakehouse_etl.py
```

**6. Serve Features for Machine Learning (Feast)**
Navigate back into the Feature Store directory. Apply the Feast configurations to build the SQLite registry, then run the handshake script to simulate a Data Scientist pulling AI-ready features.
```bash
cd feature_repo/feature_repo

# Sync the infrastructure state
feast apply

# Retrieve historically accurate features as a Pandas DataFrame
python test_workflow.py
```
*If successful, your terminal will print a clean Pandas DataFrame containing ```avg_temperature_c```, ```peak_vibration_hz```, and ```anomaly_count``` perfectly aligned with an ```event_timestamp```!*
