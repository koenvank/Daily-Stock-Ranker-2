import time
from datetime import datetime, timezone

import requests

from .config import (
    LOOKBACK_HOURS,
    PUSHSHIFT_BASE_URL,
    STOCKTWITS_BASE_URL,
    SUBREDDITS,
    PUSHSHIFT_SIZE,
    STOCKTWITS_TRENDING_LIMIT,
    STOCKTWITS_STREAM_LIMIT,
)

USER_AGENT = "reddit-stock-ranker/1.0"


def _request_json(url, params=None):
    resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _normalize_pushshift_item(item, item_type):
    return {
        "source": "pushshift",
        "subreddit": item.get("subreddit"),
        "type": item_type,
        "id": str(item.get("id")),
        "created_utc": int(item.get("created_utc", 0)),
        "author": item.get("author") or "",
        "text": (item.get("title") or "") + "\n" + (item.get("selftext") or item.get("body") or ""),
        "upvotes": int(item.get("score", 0)),
        "num_comments": int(item.get("num_comments", 0)),
        "permalink": item.get("permalink") or "",
    }


def collect_pushshift_items():
    items = []
    after = int(datetime.now(tz=timezone.utc).timestamp() - LOOKBACK_HOURS * 3600)

    for subreddit in SUBREDDITS:
        for item_type in ("submission", "comment"):
            url = f"{PUSHSHIFT_BASE_URL}/{item_type}/"
            params = {
                "subreddit": subreddit,
                "after": after,
                "size": PUSHSHIFT_SIZE,
                "sort": "desc",
                "sort_type": "created_utc",
            }
            try:
                data = _request_json(url, params=params)
                for raw in data.get("data", []):
                    items.append(_normalize_pushshift_item(raw, item_type))
            except requests.RequestException:
                continue
            time.sleep(1.0)

    return items


def _parse_stocktwits_time(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        return 0


def _normalize_stocktwits_message(message, symbol):
    return {
        "source": "stocktwits",
        "subreddit": "stocktwits",
        "type": "message",
        "id": str(message.get("id")),
        "created_utc": _parse_stocktwits_time(message.get("created_at", "")),
        "author": (message.get("user") or {}).get("username", ""),
        "text": message.get("body", ""),
        "upvotes": int((message.get("likes") or {}).get("total", 0)),
        "num_comments": 0,
        "permalink": f"https://stocktwits.com/symbol/{symbol}",
    }


def collect_stocktwits_items():
    items = []
    symbol_meta = {}
    trending_url = f"{STOCKTWITS_BASE_URL}/trending/symbols.json"
    try:
        data = _request_json(trending_url)
        symbols = [s for s in data.get("symbols", []) if s.get("symbol")]
    except requests.RequestException:
        return items, symbol_meta

    symbols = symbols[:STOCKTWITS_TRENDING_LIMIT]
    symbol_list = [s.get("symbol") for s in symbols]

    for s in symbols:
        symbol = s.get("symbol")
        if not symbol:
            continue
        symbol_meta[symbol] = {
            "name": s.get("title") or "",
            "instrument_class": s.get("instrument_class") or "",
            "exchange": s.get("exchange") or "",
        }

    for symbol in symbol_list:
        url = f"{STOCKTWITS_BASE_URL}/streams/symbol/{symbol}.json"
        params = {"limit": STOCKTWITS_STREAM_LIMIT}
        try:
            data = _request_json(url, params=params)
            for msg in data.get("messages", []):
                items.append(_normalize_stocktwits_message(msg, symbol))
        except requests.RequestException:
            continue
        time.sleep(1.0)

    return items, symbol_meta


def collect_items():
    items = []
    symbol_meta = {}
    items.extend(collect_pushshift_items())
    stocktwits_items, stocktwits_meta = collect_stocktwits_items()
    items.extend(stocktwits_items)
    symbol_meta.update(stocktwits_meta)
    return items, symbol_meta
