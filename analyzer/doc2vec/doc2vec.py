from abc import ABC, abstractmethod

# Strategy 1
import spacy
import json


class doc2vec(ABC):
    def analyze(self, body_text):
        pass

class doc2vecStrategyA(doc2vec):
    def __init__(self, model):
        self.nlp = model
    def analyze(self, body_text):
        doc = self.nlp(body_text)
        t = doc.vector.tolist()
        return json.dumps(t), doc.vector_norm

class doc2vecAnalyzer():
    def __init__(self, strategy: doc2vec):
        self._strategy = strategy
    def analyze(self, body_text):
        return self._strategy.analyze(body_text)
