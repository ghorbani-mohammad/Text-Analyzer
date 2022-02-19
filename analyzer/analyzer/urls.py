from django.urls import path

from . import views


urlpatterns = [
    path("sentiment_words/<int:news_id>/", views.SentimentWordsAPIView.as_view()),
    path("keword_extraction/", views.KeywordExtractionAPIView.as_view()),
]
