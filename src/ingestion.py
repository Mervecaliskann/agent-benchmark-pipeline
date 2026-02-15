import pandas as pd
import numpy as np
from google.cloud import bigquery
import os

# 1. SETUP AUTHENTICATION
# We use a service account key (JSON) to securely connect our local environment to Google Cloud.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# 2. DEFINE CONFIGURATIONS
# project_id, dataset, and table names are defined to point to our BigQuery Sandbox.
project_id = 'scenic-genre-425310-b9' 
client = bigquery.Client(project=project_id)
table_id = f"{project_id}.agent_benchmark_lab.simulation_logs"

def generate_agent_data(n=500):
    """
    GENERATIVE SIMULATOR: Creates synthetic logs for AI Agent performance evaluation.
    This mimics real-world production logs where we track latency and success rates.
    """
    architectures = ['ReAct', 'Plan-and-Execute']
    
    data = {
        'timestamp': pd.date_range(start='2026-02-01', periods=n, freq='h'),
        'agent_id': [f"agent_{i}" for i in range(n)],
        'architecture': np.random.choice(architectures, n),
        
        # We use a Beta distribution for success_score to reflect high-performing AI models. 
        'success_score': np.random.uniform(0.7, 0.99, n), 
        
        # Latency is simulated in milliseconds to measure system efficiency.
        'latency_ms': np.random.randint(200, 5000, n),
        
        # Reasoning steps indicate the depth of the LLM's thought process.
        'reasoning_steps': np.random.randint(2, 10, n)
    }
    return pd.DataFrame(data)

# 3. EXECUTE DATA INGESTION
print("🚀 Starting Data Ingestion Pipeline...")
df = generate_agent_data()

# WRITE_TRUNCATE ensures the table is refreshed with new data every time we run the script.
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

# The client sends the DataFrame directly to BigQuery Studio.
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result() # Wait for the job to complete.

print(f"✅ Success: {len(df)} rows uploaded to BigQuery!")