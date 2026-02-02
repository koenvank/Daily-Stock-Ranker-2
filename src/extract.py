import re

BLACKLIST = {
    "A", "I", "AN", "AND", "ARE", "AS", "AT", "BE", "BY", "CEO", "CFO", "COO",
    "DO", "FOR", "FROM", "HAS", "HAVE", "IN", "IS", "IT", "NO", "NOT", "OF",
    "ON", "OR", "THE", "TO", "USA", "USD", "YOLO", "DD", "IMO", "IDK", "ETF",
    "FED", "FOMC", "GDP", "IRA", "SEC", "IRS", "IPO", "AI",
}

DOLLAR_TICKER_RE = re.compile(r"\$[A-Z]{1,5}\b")
PLAIN_TICKER_RE = re.compile(r"\b[A-Z]{2,5}\b")


def extract_tickers(text):
    if not text:
        return []

    tickers = set()

    for match in DOLLAR_TICKER_RE.findall(text):
        ticker = match.replace("$", "")
        if ticker not in BLACKLIST:
            tickers.add(ticker)

    for match in PLAIN_TICKER_RE.findall(text):
        if match not in BLACKLIST:
            tickers.add(match)

    return sorted(tickers)
