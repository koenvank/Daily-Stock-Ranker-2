import math
from collections import defaultdict

import numpy as np

from .config import SOURCE_WEIGHTS, SUBREDDIT_WEIGHTS


def _engagement_score(upvotes, num_comments):
    return math.log1p(max(0, upvotes) + max(0, num_comments))


def _recency_decay(created_utc, now_utc):
    age_hours = max(0, (now_utc - created_utc) / 3600.0)
    return 0.5 ** (age_hours / 24.0)


def _positive_sentiment(score):
    return max(0.0, score)


def _zscore(values):
    if not values:
        return []
    arr = np.array(values, dtype=float)
    mean = arr.mean()
    std = arr.std()
    if std == 0:
        return [0.0 for _ in values]
    return ((arr - mean) / std).tolist()


def _scale_0_100(zscores):
    scaled = []
    for z in zscores:
        val = 50.0 + 15.0 * z
        scaled.append(float(min(100.0, max(0.0, val))))
    return scaled


def score_tickers(items, now_utc):
    per_ticker = defaultdict(lambda: {
        "mention_count": 0,
        "authors": set(),
        "engagement_sum": 0.0,
        "raw_core": 0.0,
        "raw_momentum": 0.0,
        "raw_conviction": 0.0,
    })

    for item in items:
        tickers = item.get("tickers", [])
        if not tickers:
            continue

        sentiment = _positive_sentiment(item.get("sentiment", 0.0))
        if sentiment <= 0:
            continue

        engagement = _engagement_score(item.get("upvotes", 0), item.get("num_comments", 0))
        decay = _recency_decay(item.get("created_utc", now_utc), now_utc)
        source_weight = SOURCE_WEIGHTS.get(item.get("source"), 1.0)
        subreddit_weight = SUBREDDIT_WEIGHTS.get(item.get("subreddit"), 1.0)
        base = sentiment * engagement * decay * source_weight * subreddit_weight

        for ticker in tickers:
            bucket = per_ticker[ticker]
            bucket["mention_count"] += 1
            bucket["authors"].add(item.get("author", ""))
            bucket["engagement_sum"] += engagement
            bucket["raw_core"] += base
            bucket["raw_momentum"] += base * 1.2

    for ticker, bucket in per_ticker.items():
        bucket["raw_conviction"] = (len(bucket["authors"]) + 1) * math.log1p(bucket["engagement_sum"]) * (1 + 0.1 * bucket["mention_count"])

    tickers = list(per_ticker.keys())
    core_raw = [per_ticker[t]["raw_core"] for t in tickers]
    momentum_raw = [per_ticker[t]["raw_momentum"] for t in tickers]
    conviction_raw = [per_ticker[t]["raw_conviction"] for t in tickers]

    core_scores = _scale_0_100(_zscore(core_raw))
    momentum_scores = _scale_0_100(_zscore(momentum_raw))
    conviction_scores = _scale_0_100(_zscore(conviction_raw))

    results = []
    for i, ticker in enumerate(tickers):
        bucket = per_ticker[ticker]
        results.append({
            "ticker": ticker,
            "core_score": core_scores[i],
            "momentum_score": momentum_scores[i],
            "conviction_score": conviction_scores[i],
            "mention_count": bucket["mention_count"],
            "unique_authors": len(bucket["authors"]),
            "engagement": float(bucket["engagement_sum"]),
        })

    return results
