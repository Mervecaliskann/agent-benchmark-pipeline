import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.express as px
from scipy import stats
import os

# 1. Page Config
st.set_page_config(page_title="AI Agent Benchmark Lab", layout="wide")
st.title("🤖 AI Agentic Benchmarking Dashboard")

# 2. Authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
client = bigquery.Client()

# 3. Data Fetching
@st.cache_data # Veriyi her seferinde çekmemek için önbelleğe alıyoruz
def load_data():
    query = "SELECT * FROM `scenic-genre-425310-b9.agent_benchmark_lab.simulation_logs`"
    return client.query(query).to_dataframe()

df = load_data()

# 4. Sidebar / Filters
st.sidebar.header("Filter Results")
selected_arch = st.sidebar.multiselect("Select Architectures", options=df['architecture'].unique(), default=df['architecture'].unique())
filtered_df = df[df['architecture'].isin(selected_arch)]

# 5. Metrics Overview
col1, col2, col3 = st.columns(3)
col1.metric("Total Simulations", len(filtered_df))
col2.metric("Avg Success Score", f"{filtered_df['success_score'].mean():.2%}")
col3.metric("Avg Latency (ms)", f"{filtered_df['latency_ms'].mean():.0f}")

# 6. Visualizations
st.subheader("Performance Comparison")
fig_box = px.box(filtered_df, x="architecture", y="success_score", color="architecture", title="Success Score Distribution")
st.plotly_chart(fig_box, use_container_width=True)

# 7. Statistical Test Results
st.subheader("Statistical Validation (ANOVA)")
react_scores = df[df['architecture'] == 'ReAct']['success_score']
plan_scores = df[df['architecture'] == 'Plan-and-Execute']['success_score']
f_stat, p_val = stats.f_oneway(react_scores, plan_scores)

st.write(f"**F-Statistic:** {f_stat:.4f} | **P-Value:** {p_val:.4f}")
if p_val < 0.05:
    st.success("✅ Statistically Significant difference detected!")
else:
    st.info("ℹ️ No statistically significant difference found (p > 0.05).")