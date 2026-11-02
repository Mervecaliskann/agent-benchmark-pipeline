"""
Shared benchmark question set for both agent architectures.

Ported verbatim from finance-agent-langgraph/eval.py so that ReAct and
Plan-and-Execute are evaluated on the exact same 14 questions.
"""

TEST_CASES = [
    {"question": "What is the current price of Apple?", "expected_tools": ["get_stock_price"]},
    {"question": "Compare the PE ratio of Google and Meta.", "expected_tools": ["get_company_fundamentals"]},
    {"question": "Give me a fundamental analysis of Tesla.", "expected_tools": ["get_company_fundamentals"]},
    {"question": "What's today's daily change percentage for Microsoft stock?", "expected_tools": ["get_stock_price"]},
    {"question": "Tell me about Amazon's market cap and sector.", "expected_tools": ["get_company_fundamentals"]},
    {"question": "How is THYAO.IS performing today?", "expected_tools": ["get_stock_price"]},
    {"question": "What is the 52 week high for Nvidia?", "expected_tools": ["get_company_fundamentals"]},
    {"question": "Compare the current prices of Apple and Microsoft.", "expected_tools": ["get_stock_price"]},
    {"question": "Based on today's price movement, is Tesla stock volatile right now?", "expected_tools": ["get_stock_price"]},
    {"question": "What sector does Netflix operate in?", "expected_tools": ["get_company_fundamentals"]},
    {"question": "Give me both the price and fundamentals for Coca-Cola.", "expected_tools": ["get_stock_price", "get_company_fundamentals"]},
    {"question": "What is the market cap of Meta?", "expected_tools": ["get_company_fundamentals"]},
    {"question": "Give me the current price of Google stock.", "expected_tools": ["get_stock_price"]},
    {"question": "Provide a full analysis (price and fundamentals) of Amazon.", "expected_tools": ["get_stock_price", "get_company_fundamentals"]},
]


def tool_selection_correct(expected: list, actual: list) -> bool:
    """True if every expected tool was called at least once (extra calls are OK)."""
    return set(expected).issubset(set(actual))
