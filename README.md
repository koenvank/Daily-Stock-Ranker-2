# Reddit + Stocktwits Daily Stock Sentiment Ranker

Lightweight daily ranking of stocks using public Reddit data via Pushshift and Stocktwits messages. No API keys required.

## What it does
- Collects recent Reddit posts/comments from investing subreddits via Pushshift
- Collects Stocktwits messages for trending symbols
- Extracts stock tickers from text
- Runs VADER sentiment and keeps only positive sentiment
- Scores tickers with engagement, recency decay, and sentiment
- Applies do-not-buy filters and labels tickers (TRADE/WATCH/IGNORE)
- Outputs a daily CSV with the Top 5 stocks and a `latest.json` for the GUI

> Important: This is **not** investment advice. Sentiment is only an attention signal.

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment overrides in `.env` (see `.env.example`).

## Run
```bash
python -m src.run_daily
```

## Outputs
- Daily CSV: `data/reports/report_YYYY-MM-DD.csv`
- Latest JSON for GUI: `data/reports/latest.json`
- GitHub Pages copy: `docs/data/latest.json`
- SQLite database: `data/reddit.db`

## GUI (GitHub Pages)
The static GUI is in `docs/` and reads `docs/data/latest.json`.

To enable GitHub Pages:
1. In your repo settings, enable Pages and choose the GitHub Actions workflow or the `/docs` folder.
2. The workflow `.github/workflows/daily.yml` runs daily and on manual dispatch, updates the data files, and deploys Pages.

## Filter modes
- **balanced**: excludes leveraged/inverse ETFs, keeps pump-risk tickers but marks them.
- **strict**: excludes leveraged/inverse ETFs and pump-risk tickers.

You can change the default mode via `FILTER_MODE` in `.env`.
