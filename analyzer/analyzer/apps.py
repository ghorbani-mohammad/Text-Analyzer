import spacy
from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    name = "analyzer"
    spacy_model = spacy.load("en_core_web_md")
