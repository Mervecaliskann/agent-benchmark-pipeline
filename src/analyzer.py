import pandas as pd
from google.cloud import bigquery
from scipy import stats
import os

# 1. SETUP: Secure Authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
client = bigquery.Client()

# 2. DATA ACQUISITION
query = "SELECT architecture, success_score FROM `scenic-genre-425310-b9.agent_benchmark_lab.simulation_logs`"
df = client.query(query).to_dataframe()

react_scores = df[df['architecture'] == 'ReAct']['success_score']
plan_scores = df[df['architecture'] == 'Plan-and-Execute']['success_score']

def run_rigorous_analysis(group1, group2):
    print("="*50)
    print("🛡️ ASSUMPTION TESTING (Statistician Rigor)")
    print("="*50)

    # A. Normality Test (Shapiro-Wilk)
    # H0: Data follows a normal distribution
    _, p_norm1 = stats.shapiro(group1)
    _, p_norm2 = stats.shapiro(group2)
    
    print(f"Normality (ReAct) p-value: {p_norm1:.4f}")
    print(f"Normality (Plan) p-value:  {p_norm2:.4f}")

    # B. Homogeneity of Variance (Levene's Test)
    # H0: Variances are equal across groups
    _, p_levene = stats.levene(group1, group2)
    print(f"Variance Equality p-value: {p_levene:.4f}")
    print("-" * 50)

    # 3. DECISION LOGIC
    if p_norm1 > 0.05 and p_norm2 > 0.05 and p_levene > 0.05:
        print("✅ Assumptions MET: Running Parametric ANOVA...")
        f_stat, p_val = stats.f_oneway(group1, group2)
        test_name = "One-Way ANOVA"
    else:
        print("⚠️ Assumptions VIOLATED: Running Non-Parametric Kruskal-Wallis...")
        f_stat, p_val = stats.kruskal(group1, group2)
        test_name = "Kruskal-Wallis H-Test"

    print(f"\nFINAL RESULT ({test_name})")
    print(f"Statistic: {f_stat:.4f} | P-Value: {p_val:.4f}")
    
    if p_val < 0.05:
        print("📢 Result: STATISTICALLY SIGNIFICANT difference.")
    else:
        print("📢 Result: NO significant difference detected.")

run_rigorous_analysis(react_scores, plan_scores)