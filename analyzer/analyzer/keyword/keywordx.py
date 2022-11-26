from abc import ABC

from analyzer.apps import AnalyzerConfig


class Keyword(ABC):
    def analyze(self, body_text):
        pass


class KeywordStrategyA(Keyword):
    def analyze(self, body_text, limit):
        from rake_nltk import Rake
        from nltk.corpus import stopwords

        r = Rake(min_length=1, max_length=1)
        r.extract_keywords_from_text(body_text)
        return r.get_ranked_phrases()[:limit]


class KeywordStrategyB(Keyword):
    import spacy
    from collections import Counter
    from string import punctuation

    def analyze(self, body_text, limit):
        nlp = AnalyzerConfig.spacy_model
        result = []
        pos_tag = ["PROPN", "NOUN"]
        doc = nlp(body_text.lower())
        for token in doc:
            if token.text in nlp.Defaults.stop_words or token.text in punctuation:
                continue
            if token.pos_ in pos_tag:
                result.append(token.text)
        return [x[0] for x in Counter(result).most_common(limit)]


class KeywordStrategyC(Keyword):
    def analyze(self, body_text, limit):
        from gensim.summarization import keywords

        return keywords(body_text, words=10, lemmatize=True, deacc=True, split=True)


class KeywordStrategyD(Keyword):
    def analyze(self, body_text, limit):
        from gensim.summarization import keywords
        from nltk.stem import WordNetLemmatizer

        wordnet_lemmatizer = WordNetLemmatizer()
        results = keywords(body_text, words=10, lemmatize=True, deacc=True, split=True)
        return [wordnet_lemmatizer.lemmatize(w) for w in results]


class KeywordAnalyzer:
    def __init__(self, strategy: Keyword, limit):
        self._strategy = strategy
        self._limit = limit

    def analyze(self, body_text):
        return self._strategy.analyze(body_text, self._limit)
