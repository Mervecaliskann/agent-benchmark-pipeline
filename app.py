import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.express as px
from scipy import stats
import os

# 1. Page Config & Professional Branding
st.set_page_config(page_title="Scientific AI Benchmarking", layout="wide")
st.title("🔬 AI Agentic Benchmarking & Statistical Lab")
st.markdown("---")

# 2. Authentication & Data Fetching
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
client = bigquery.Client()

@st.cache_data
def load_data():
    query = "SELECT * FROM `scenic-genre-425310-b9.agent_benchmark_lab.simulation_logs`"
    return client.query(query).to_dataframe()

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Control Panel")
selected_arch = st.sidebar.multiselect("Select Architectures", options=df['architecture'].unique(), default=df['architecture'].unique())
filtered_df = df[df['architecture'].isin(selected_arch)]

# 4. Metrics Overview
col1, col2, col3 = st.columns(3)
col1.metric("Total Simulations", len(filtered_df))
col2.metric("Avg Success Score", f"{filtered_df['success_score'].mean():.2%}")
col3.metric("Avg Latency (ms)", f"{filtered_df['latency_ms'].mean():.0f}")

# 5. Visualizations
st.subheader("Performance Distribution Analysis")
fig_box = px.box(filtered_df, x="architecture", y="success_score", color="architecture", 
                 points="all", title="Success Score: Distribution and Outliers")
st.plotly_chart(fig_box, use_container_width=True)

# 6. STATISTICAL RIGOR SECTION (The Scientist's Signature)
st.markdown("---")
st.subheader("🛡️ Statistical Assumption Testing & Hypothesis Validation")

react_scores = df[df['architecture'] == 'ReAct']['success_score']
plan_scores = df[df['architecture'] == 'Plan-and-Execute']['success_score']

# A. Assumption Checks
with st.expander("View Assumption Details (Shapiro-Wilk & Levene)"):
    _, p_norm1 = stats.shapiro(react_scores)
    _, p_norm2 = stats.shapiro(plan_scores)
    _, p_levene = stats.levene(react_scores, plan_scores)
    
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Normality (ReAct):** p={p_norm1:.4f}")
    c2.write(f"**Normality (Plan):** p={p_norm2:.4f}")
    c3.write(f"**Variance Equality:** p={p_levene:.4f}")

# B. Adaptive Test Selection Logic 
normality_passed = p_norm1 > 0.05 and p_norm2 > 0.05
variance_passed = p_levene > 0.05

if normality_passed and variance_passed:
    test_name = "One-Way ANOVA (Parametric)"
    f_stat, p_val = stats.f_oneway(react_scores, plan_scores)
    st.info(f"✅ Assumptions met. Running **{test_name}**.")
else:
    test_name = "Kruskal-Wallis H-Test (Non-Parametric)"
    f_stat, p_val = stats.kruskal(react_scores, plan_scores)
    st.warning(f"⚠️ Normality or Variance assumptions violated. Automatically switched to **{test_name}**.")

# 7. Final Statistical Result
st.subheader(f"Final Statistical Result: {test_name}")
st.write(f"**Test Statistic:** {f_stat:.4f} | **P-Value:** {p_val:.4f}")

if p_val < 0.05:
    st.success("🎯 **Conclusion:** Statistically Significant difference detected! Model selection should favor the higher-performing architecture.")
else:
    st.info("ℹ️ **Conclusion:** No statistically significant difference found. Choice can be driven by cost or latency.")