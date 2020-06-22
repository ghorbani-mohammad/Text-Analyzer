from django.urls import path, include
from rest_framework import routers

from .views import SentimentWords


urlpatterns = [
    path('sentiment_words/<int:news_id>/', SentimentWords.as_view()),
]
