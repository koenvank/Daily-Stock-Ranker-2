from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_ANALYZER = SentimentIntensityAnalyzer()


def sentiment_score(text):
    if not text:
        return 0.0
    return float(_ANALYZER.polarity_scores(text).get("compound", 0.0))
