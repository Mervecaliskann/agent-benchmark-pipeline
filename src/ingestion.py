import os
import sys
import time

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

from agents.test_cases import TEST_CASES, tool_selection_correct
from agents import react_agent
from agents import langgraph_agent

# Windows consoles default to a non-UTF-8 codepage that can't encode emoji.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. SETUP AUTHENTICATION
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
if not os.getenv("GROQ_API_KEY"):
    raise SystemExit("HATA: .env dosyasinda GROQ_API_KEY bulunamadi!")

# 2. DEFINE CONFIGURATIONS
project_id = 'scenic-genre-425310-b9'
client = bigquery.Client(project=project_id)
table_id = f"{project_id}.agent_benchmark_lab.simulation_logs"

# Groq's free tier caps usage at a fixed token budget per day (observed: ~100k
# TPD, ~1100 tokens/run -> ~89 runs/day). 3 reps keeps the full sweep
# (14 questions x 3 reps x 2 architectures = 84 runs) inside that budget.
REPS_PER_QUESTION = 3


class QuotaExceededError(Exception):
    """Raised when the Groq API rejects a call for hitting a rate/token quota."""


def _is_quota_error(e: Exception) -> bool:
    msg = str(e)
    return "rate_limit_exceeded" in msg or "429" in msg or "Rate limit reached" in msg


def run_react(question: str, expected_tools: list) -> tuple:
    start = time.time()
    try:
        result = react_agent.run(question)
    except Exception as e:
        if _is_quota_error(e):
            raise QuotaExceededError(str(e)) from e
        latency_ms = (time.time() - start) * 1000
        print(f"    [ReAct] ERROR: {e}")
        return 0.0, latency_ms, 0

    latency_ms = (time.time() - start) * 1000
    success = 1.0 if tool_selection_correct(expected_tools, result["tools_called"]) else 0.0
    return success, latency_ms, result["reasoning_steps"]


def run_plan_execute(question: str, expected_tools: list) -> tuple:
    start = time.time()
    try:
        result = langgraph_agent.run(question)
    except Exception as e:
        if _is_quota_error(e):
            raise QuotaExceededError(str(e)) from e
        latency_ms = (time.time() - start) * 1000
        print(f"    [Plan-and-Execute] ERROR: {e}")
        return 0.0, latency_ms, 0

    latency_ms = (time.time() - start) * 1000
    success = 1.0 if tool_selection_correct(expected_tools, result["tools_called"]) else 0.0
    # The graph always traverses fetch_data -> analyze -> generate_report;
    # human_review is inserted only when analyze flags risk_level == "high".
    reasoning_steps = 4 if result.get("risk_level") == "high" else 3
    return success, latency_ms, reasoning_steps


RUNNERS = {
    "ReAct": run_react,
    "Plan-and-Execute": run_plan_execute,
}


def collect_real_agent_data(reps: int = REPS_PER_QUESTION) -> pd.DataFrame:
    """
    REAL AGENT BENCHMARK: Runs both agent architectures on the same 14
    finance questions (src/agents/test_cases.py), `reps` times each, with
    real Groq API calls. Each row is one real run, not a simulated sample.
    """
    rows = []
    total_runs = reps * len(TEST_CASES) * len(RUNNERS)
    run_idx = 0

    for rep in range(reps):
        for q_idx, case in enumerate(TEST_CASES, start=1):
            for architecture, runner in RUNNERS.items():
                run_idx += 1
                print(f"[{run_idx}/{total_runs}] rep={rep+1} q={q_idx} {architecture}: {case['question']}")

                try:
                    success, latency_ms, reasoning_steps = runner(case["question"], case["expected_tools"])
                except QuotaExceededError as e:
                    print(
                        f"\n[QUOTA EXCEEDED] Groq daily token budget hit after {len(rows)} real runs. "
                        f"Stopping now and keeping only the {len(rows)} valid runs collected so far "
                        f"(no fabricated failure rows). Re-run later to collect the rest.\n  {e}"
                    )
                    return pd.DataFrame(rows)

                print(f"    success={success} latency_ms={latency_ms:.0f} reasoning_steps={reasoning_steps}")

                rows.append({
                    "timestamp": pd.Timestamp.utcnow(),
                    "agent_id": f"{architecture}_q{q_idx}_r{rep+1}",
                    "architecture": architecture,
                    "success_score": success,
                    "latency_ms": int(round(latency_ms)),
                    "reasoning_steps": reasoning_steps,
                })

    return pd.DataFrame(rows)


# 3. EXECUTE DATA INGESTION
print("🚀 Starting Real Agent Benchmark Pipeline...")
df = collect_real_agent_data()

if df.empty:
    raise SystemExit("HATA: Hicbir gercek calistirma tamamlanamadi, BigQuery'e yuklenecek veri yok.")

# WRITE_TRUNCATE ensures the table is refreshed with new data every time we run the script.
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()  # Wait for the job to complete.

print(f"✅ Success: {len(df)} real agent benchmark rows uploaded to BigQuery!")
