# from keywordx import *
from analyzer.keyword.keywordx import *


def analyzeKeyword(news_id, text, limit, algo):

    if algo == "rake":
        keyword_analyzer = KeywordAnalyzer(KeywordStrategyA(), limit)
        keywords = keyword_analyzer.analyze(text)
    elif algo == "spacy":
        keyword_analyzer = KeywordAnalyzer(KeywordStrategyB(), limit)
        keywords = keyword_analyzer.analyze(text)
    elif algo == "gensim":
        keyword_analyzer = KeywordAnalyzer(KeywordStrategyC(), limit)
        keywords = keyword_analyzer.analyze(text)
    elif algo == "gensimWithWordNet":
        keyword_analyzer = KeywordAnalyzer(KeywordStrategyD(), limit)
        keywords = keyword_analyzer.analyze(text)
    
    return keywords