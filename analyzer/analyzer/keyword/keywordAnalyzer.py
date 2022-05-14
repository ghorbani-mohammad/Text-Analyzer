from analyzer.keyword.keywordx import *


def analyzeKeyword(text, limit, algo):
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
    ignore_list = ["said", "news", "new", "case", "state", "city", "State"]
    return [keyword for keyword in keywords if keyword not in ignore_list]
