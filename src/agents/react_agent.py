"""
ReAct tool-calling agent - headless port of AI-Finance-Agent/app.py.

Same tools, same LLM config, and same prompt as the original Streamlit app;
only the Streamlit UI layer is removed so the agent can be invoked
programmatically for benchmarking (mirrors the langgraph_agent.run() interface).
"""

import os

import yfinance as yf
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


@tool
def get_stock_price(ticker: str):
    """
    Retrieves the current stock price and daily change percentage.
    Input example: 'AAPL', 'TSLA', 'THYAO.IS' (for Turkish stocks).
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        if history.empty:
            return {"error": "Veri bulunamadı. Sembolü kontrol et."}

        current_price = history['Close'].iloc[-1]
        open_price = history['Open'].iloc[-1]
        change_percent = ((current_price - open_price) / open_price) * 100

        return {
            "symbol": ticker.upper(),
            "price": f"{current_price:.2f}",
            "change_percent": f"%{change_percent:.2f}"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_company_fundamentals(ticker: str):
    """
    Retrieves fundamental financial data like Market Cap, P/E Ratio, and Sector.
    Use this when the user asks for 'analysis', 'details', or 'company info'.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "Company": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "P/E Ratio": info.get("trailingPE", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "Summary": info.get("longBusinessSummary", "")[:300] + "..."
        }
    except Exception as e:
        return {"error": str(e)}


TOOLS = [get_stock_price, get_company_fundamentals]


def build_agent_executor() -> AgentExecutor:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a Senior Financial Analyst AI. "
            "Your goal is to provide accurate market data and insights. "
            "Use the provided tools to fetch real-time data from Yahoo Finance. "
            "Always be professional, concise, and data-driven. "
            "If you calculate something, explain your logic. "
            "Do NOT make up numbers. Only use data from tools."
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    # return_intermediate_steps=True only changes what invoke() returns, not
    # the agent's behavior - needed to count real tool calls for benchmarking.
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=False, return_intermediate_steps=True)


_EXECUTOR = None


def get_executor() -> AgentExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = build_agent_executor()
    return _EXECUTOR


def run(question: str) -> dict:
    """Run a single question through the ReAct agent."""
    executor = get_executor()
    response = executor.invoke({"input": question})
    intermediate_steps = response.get("intermediate_steps", [])
    tools_called = [action.tool for action, _observation in intermediate_steps]

    return {
        "tools_called": tools_called,
        "report": response.get("output", ""),
        "reasoning_steps": len(intermediate_steps),
    }


if __name__ == "__main__":
    import sys

    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("HATA: .env dosyasinda GROQ_API_KEY bulunamadi!")

    question = " ".join(sys.argv[1:]) or "What is the current price of Apple?"
    result = run(question)

    print(f"Question: {question}")
    print(f"Tools called: {result['tools_called']}")
    print(f"Reasoning steps: {result['reasoning_steps']}")
    print(f"\nReport:\n{result['report']}")
