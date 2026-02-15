# 🤖 AI Agentic Benchmarking Pipeline

An end-to-end evaluation framework designed to benchmark and statistically validate the performance of different AI Agent architectures (ReAct vs. Plan-and-Execute).

## 🚀 Overview
This project serves as a simulation of a real-world scientific intelligence lab workflow. It automates the collection of agent logs, processes them in **Google BigQuery**, and provides a statistical decision-making layer through a **Streamlit** dashboard.

## 📊 Dashboard Preview
![Dashboard Preview](assets/dashboard_review.png)

## 🛠 Tech Stack
- **Data Infrastructure:** Google BigQuery (Cloud Data Warehouse)
- **Programming:** Python (Pandas, Numpy)
- **Statistical Analysis:** SciPy (One-Way ANOVA), Scikit-learn
- **Visualization:** Streamlit, Plotly Express

## 🔬 Scientific Validation
The core of this framework is the **Statistical Evaluation Layer**. Instead of relying on raw averages, it employs **One-Way ANOVA** to determine if performance differences between architectures are statistically significant ($p < 0.05$). 

In the current simulation, the $p\text{-value}$ was found to be **0.5490**, suggesting that both architectures perform similarly under current constraints, leading to a data-driven decision based on latency and cost.