from analyzer.doc2vec.doc2vec import *


def analyzeDoc2vec(news_id, text, now, config):
    if config == "spacy":
        doc2vec_analyzer = doc2vecAnalyzer(doc2vecStrategyA())
        vector, vector_norm = doc2vec_analyzer.analyze(text)
    else:
        doc2vec_analyzer = doc2vecAnalyzer(doc2vecStrategyA())
        vector, vector_norm = doc2vec_analyzer.analyze(text)

    return vector, vector_norm
