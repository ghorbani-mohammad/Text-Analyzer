from analyzer.sentiment.sentiment import *


def analyzeSentiment(news_id, body_text, now, config):
    if config == "nltk":
        sentiment_analyzer = SentimentAnalyzer(SentimentStrategyA())
        x = sentiment_analyzer.analyze(body_text)
    elif config == "textblob":
        sentiment_analyzer = SentimentAnalyzer(SentimentStrategyB())
        x = sentiment_analyzer.analyze(body_text)
    else:
        sentiment_analyzer = SentimentAnalyzer(SentimentStrategyA())
        x = sentiment_analyzer.analyze(body_text)
    return x 
    