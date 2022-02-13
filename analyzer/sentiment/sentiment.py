from abc import ABC, abstractmethod

# Strategy A
import nltk

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Strategy B
from textblob import TextBlob


class Sentiment(ABC):
    def analyze(self, body_text):
        pass


class SentimentStrategyA(Sentiment):
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def analyze(self, body_text):
        return self.sid.polarity_scores(body_text)


class SentimentStrategyB(Sentiment):
    def analyze(self, body_text):
        return TextBlob(body_text).sentiment


class SentimentAnalyzer:
    def __init__(self, strategy: Sentiment):
        self._strategy = strategy

    def strategy(self):
        return self._strategy

    def analyze(self, body_text):
        return self._strategy.analyze(body_text)
