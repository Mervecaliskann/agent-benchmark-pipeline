import pandas as pd
from google.cloud import bigquery
from scipy import stats
import os

# 1. SETUP: Pointing to our cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
client = bigquery.Client()

# 2. DATA RETRIEVAL: Pulling simulation logs from BigQuery Studio
# We use SQL to bring our cloud data back into a Python DataFrame for analysis.
query = """
    SELECT architecture, success_score 
    FROM `scenic-genre-425310-b9.agent_benchmark_lab.simulation_logs`
"""
df = client.query(query).to_dataframe()

# 3. STATISTICAL ANALYSIS: One-Way ANOVA
# We test if the mean success_score of 'ReAct' is significantly different from 'Plan-and-Execute'.
react_scores = df[df['architecture'] == 'ReAct']['success_score']
plan_scores = df[df['architecture'] == 'Plan-and-Execute']['success_score']

# f_oneway performs the ANOVA test to check if the means are statistically different.
f_stat, p_val = stats.f_oneway(react_scores, plan_scores)

print("\n" + "="*40)
print("📊 STATISTICAL BENCHMARK REPORT")
print("="*40)
print(f"F-Statistic: {f_stat:.4f}")
print(f"P-Value:     {p_val:.4f}")
print("-" * 40)

# 4. INTERPRETATION: Decision Making based on P-Value
# In Data Science, a p-value < 0.05 usually indicates 'Statistical Significance'.
if p_val < 0.05:
    print("📢 CONCLUSION: The difference is STATISTICALLY SIGNIFICANT.")
    print("Strategic Insight: One architecture clearly outperforms the other.")
else:
    print("📢 CONCLUSION: The difference is NOT statistically significant.")
    print("Strategic Insight: Both architectures perform similarly; choice can be based on cost/latency.")
print("="*40 + "\n")