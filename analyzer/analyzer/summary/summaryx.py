def extractSummary(
    PlaintextParser, Tokenizer, Stemmer, Summarizer, get_stop_words, body
):
    LANGUAGE = "english"
    SENTENCES_COUNT = 1

    parser = PlaintextParser.from_string(body, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sentence = summarizer(parser.document, SENTENCES_COUNT)

    return sentence
