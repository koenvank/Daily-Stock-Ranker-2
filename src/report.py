import json
import os
from datetime import datetime, timezone

import pandas as pd

from .config import REPORT_DIR, DOCS_DATA_DIR


def write_daily_report(scores, day=None):
    if day is None:
        day = datetime.now(tz=timezone.utc).date().isoformat()

    os.makedirs(REPORT_DIR, exist_ok=True)

    top = sorted(scores, key=lambda s: s.get("momentum_score", 0), reverse=True)[:5]
    df = pd.DataFrame(top, columns=[
        "ticker",
        "label",
        "risk_tag",
        "momentum_score",
        "conviction_score",
        "core_score",
        "mention_count",
        "unique_authors",
        "engagement",
    ])

    path = os.path.join(REPORT_DIR, f"report_{day}.csv")
    df.to_csv(path, index=False)
    return path, df


def write_latest_json(scores, generated_utc, filter_mode_default="balanced"):
    payload = {
        "generated_utc": int(generated_utc),
        "filter_mode_default": filter_mode_default,
        "rows": [],
    }

    for row in scores:
        payload["rows"].append({
            "ticker": row.get("ticker"),
            "momentum_score": float(row.get("momentum_score", 0.0)),
            "conviction_score": float(row.get("conviction_score", 0.0)),
            "core_score": float(row.get("core_score", 0.0)),
            "mention_count": int(row.get("mention_count", 0)),
            "unique_authors": int(row.get("unique_authors", 0)),
            "engagement": float(row.get("engagement", 0.0)),
            "label": row.get("label"),
            "risk_tag": row.get("risk_tag", ""),
        })

    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(DOCS_DATA_DIR, exist_ok=True)

    latest_path = os.path.join(REPORT_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    docs_latest = os.path.join(DOCS_DATA_DIR, "latest.json")
    with open(docs_latest, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    return latest_path, docs_latest
