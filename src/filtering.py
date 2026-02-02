import re

from .config import (
    DENYLIST_TICKERS,
    DENYLIST_KEYWORDS,
    FILTER_MODE,
    PUMP_LOW_AUTHORS_MAX,
    PUMP_LOW_MENTIONS_MAX,
    PUMP_HIGH_MOMENTUM_MIN,
)

SUSPICIOUS_TICKER_RE = re.compile(r"^[A-Z]{4,5}$")


def _keyword_hit(text):
    if not text:
        return False
    lower = text.lower()
    return any(k in lower for k in DENYLIST_KEYWORDS)


def _is_leveraged_inverse(ticker, meta):
    if ticker in DENYLIST_TICKERS:
        return True
    if not meta:
        return False
    return _keyword_hit(meta.get("name")) or _keyword_hit(meta.get("instrument_class"))


def _is_suspicious_ticker(ticker):
    if ticker in DENYLIST_TICKERS:
        return True
    if not SUSPICIOUS_TICKER_RE.match(ticker):
        return False
    if ticker.endswith("W"):
        return True
    for ch in set(ticker):
        if ticker.count(ch) >= 3:
            return True
    return False


def _is_pump_risk(score):
    return (
        score.get("unique_authors", 0) <= PUMP_LOW_AUTHORS_MAX
        and score.get("mention_count", 0) <= PUMP_LOW_MENTIONS_MAX
        and score.get("momentum_score", 0) >= PUMP_HIGH_MOMENTUM_MIN
    )


def apply_filters(scores, ticker_meta, filter_mode=None):
    mode = filter_mode or FILTER_MODE
    filtered = []

    for score in scores:
        ticker = score.get("ticker")
        meta = ticker_meta.get(ticker, {})

        leveraged = _is_leveraged_inverse(ticker, meta)
        pump_risk = _is_pump_risk(score) or _is_suspicious_ticker(ticker)

        risk_tag = ""
        if leveraged:
            risk_tag = "LEVERAGED/INVERSE"
        elif pump_risk:
            risk_tag = "PUMP_RISK"

        strict_excluded = leveraged or pump_risk
        balanced_excluded = leveraged

        if mode == "strict" and strict_excluded:
            continue
        if mode == "balanced" and balanced_excluded:
            continue

        row = dict(score)
        row["risk_tag"] = risk_tag if strict_excluded else ""
        row["strict_excluded"] = strict_excluded
        filtered.append(row)

    return filtered


def label_rows(rows):
    labeled = []
    for row in rows:
        momentum = row.get("momentum_score", 0)
        conviction = row.get("conviction_score", 0)
        mentions = row.get("mention_count", 0)
        authors = row.get("unique_authors", 0)

        if row.get("strict_excluded"):
            label = "IGNORE"
        elif momentum >= 85 and mentions >= 8 and authors >= 6:
            label = "TRADE"
        elif conviction >= 75 and authors >= 6:
            label = "WATCH"
        elif 70 <= momentum < 85 and authors >= 6:
            label = "WATCH"
        else:
            label = "IGNORE"

        out = dict(row)
        out["label"] = label
        labeled.append(out)

    return labeled
