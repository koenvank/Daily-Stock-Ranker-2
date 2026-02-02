import os
import sqlite3

from .config import DB_PATH


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_items (
                id TEXT PRIMARY KEY,
                source TEXT,
                subreddit TEXT,
                type TEXT,
                created_utc INTEGER,
                author TEXT,
                text TEXT,
                upvotes INTEGER,
                num_comments INTEGER,
                permalink TEXT,
                tickers TEXT,
                sentiment REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_scores (
                day TEXT,
                ticker TEXT,
                core_score REAL,
                momentum_score REAL,
                conviction_score REAL,
                mention_count INTEGER,
                unique_authors INTEGER,
                engagement REAL,
                PRIMARY KEY (day, ticker)
            )
            """
        )
        conn.commit()


def upsert_raw(items):
    if not items:
        return
    with _connect() as conn:
        cur = conn.cursor()
        rows = []
        for item in items:
            uid = f"{item.get('source')}:{item.get('id')}"
            rows.append(
                (
                    uid,
                    item.get("source"),
                    item.get("subreddit"),
                    item.get("type"),
                    item.get("created_utc"),
                    item.get("author"),
                    item.get("text"),
                    item.get("upvotes"),
                    item.get("num_comments"),
                    item.get("permalink"),
                    ",".join(item.get("tickers", [])),
                    float(item.get("sentiment", 0.0)),
                )
            )
        cur.executemany(
            """
            INSERT OR REPLACE INTO raw_items
            (id, source, subreddit, type, created_utc, author, text, upvotes, num_comments, permalink, tickers, sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()


def upsert_daily(day, scores):
    if not scores:
        return
    with _connect() as conn:
        cur = conn.cursor()
        rows = []
        for score in scores:
            rows.append(
                (
                    day,
                    score.get("ticker"),
                    score.get("core_score"),
                    score.get("momentum_score"),
                    score.get("conviction_score"),
                    score.get("mention_count"),
                    score.get("unique_authors"),
                    score.get("engagement"),
                )
            )
        cur.executemany(
            """
            INSERT OR REPLACE INTO daily_scores
            (day, ticker, core_score, momentum_score, conviction_score, mention_count, unique_authors, engagement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
