import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import views

from .models import News
from .keyword.social_keyword import analyze_files


class SentimentWordsAPIView(views.APIView):
    def get(self, request, version, news_id):
        document = get_object_or_404(News, id=news_id)
        nltk.download("vader_lexicon")
        nltk.download("punkt")
        nltk.download("stopwords")
        analyzer = SentimentIntensityAnalyzer()
        text_tokens = nltk.word_tokenize(document.body)
        tokens_without_sw = [
            word for word in text_tokens if not word in stopwords.words()
        ]
        tokens_without_sw = [
            word.lower() for word in tokens_without_sw if word.isalpha()
        ]
        pos_word_list = []
        neu_word_list = []
        neg_word_list = []
        for word in tokens_without_sw:
            score = analyzer.polarity_scores(word)["compound"]
            if (score) > 0:
                pos_word_list.append((word, score))
            elif (score) < 0:
                neg_word_list.append((word, score))
            else:
                neu_word_list.append((word, score))
        return Response(
            {"positive": set(pos_word_list), "negative": set(neg_word_list)}
        )


class KeywordExtractionAPIView(views.APIView):
    def post(self, request, version):
        print(request.data)
        x, y = analyze_files(request.data["body"])
        print(x, y)
        return Response()
