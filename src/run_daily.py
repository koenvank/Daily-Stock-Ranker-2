from datetime import datetime, timezone

from dotenv import load_dotenv

from .collect import collect_items
from .extract import extract_tickers
from .filtering import apply_filters, label_rows
from .sentiment import sentiment_score
from .score import score_tickers
from .store import init_db, upsert_raw, upsert_daily
from .report import write_daily_report, write_latest_json
from .config import FILTER_MODE


def main():
    load_dotenv()
    init_db()

    items, ticker_meta = collect_items()
    enriched = []
    for item in items:
        tickers = extract_tickers(item.get("text", ""))
        if not tickers:
            continue
        item["tickers"] = tickers
        item["sentiment"] = sentiment_score(item.get("text", ""))
        enriched.append(item)

    now_dt = datetime.now(tz=timezone.utc)
    now_utc = int(now_dt.timestamp())
    scores = score_tickers(enriched, now_utc)

    filtered_default = apply_filters(scores, ticker_meta, filter_mode=FILTER_MODE)
    labeled_default = label_rows(filtered_default)

    filtered_balanced = apply_filters(scores, ticker_meta, filter_mode="balanced")
    labeled_balanced = label_rows(filtered_balanced)

    day = now_dt.date().isoformat()
    upsert_raw(enriched)
    upsert_daily(day, labeled_default)

    report_path, df = write_daily_report(labeled_default, day=day)
    write_latest_json(labeled_balanced, generated_utc=now_utc, filter_mode_default="balanced")

    print("Top 5 Stocks (Momentum)")
    if df.empty:
        print("No data collected.")
    else:
        print(df.to_string(index=False))
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
