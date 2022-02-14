import spacy
import time
from geopy.geocoders import Nominatim
from datetime import datetime as dt
from analyzer.apps import AnalyzerConfig


class NameEntityRecognition:
    def __init__(self, news_id, news_body, news_date, types):
        self.news_body = news_body
        self.news_id = news_id
        self.news_date = news_date
        self.nlp = AnalyzerConfig.spacy_model
        self.types = types
        self.results = None

    def find_NER_tag(self, now):
        self.results = {
            "person": [],
            "FAC": [],
            "ORG": [],
            "GPE": [],
            "LOC": [],
            "EVENT": [],
            "MONEY": [],
        }
        doc = self.nlp(self.news_body)
        for entity in doc.ents:
            if (entity.label_ == "PERSON") and (
                entity.text not in self.results["person"]
            ):
                if "person" in self.types:
                    self.results["person"].append(entity.text)
            elif (entity.label_ == "FAC") and (
                entity.text not in self.results["FAC"]
            ):  # Buildings, airports, highways, bridges, etc,
                if "fac" in self.types:
                    self.results["FAC"].append(entity.text)
            elif (entity.label_ == "ORG") and (
                entity.text not in self.results["ORG"]
            ):  # Companies, agencies, institutions, etc.
                if "org" in self.types:
                    self.results["ORG"].append(entity.text)
            elif (entity.label_ == "GPE") and (
                entity.text not in self.results["GPE"]
            ):  # Countries, cities, states.
                if "gpe" in self.types:
                    self.results["GPE"].append(entity.text)
            elif (entity.label_ == "LOC") and (
                entity.text not in self.results["LOC"]
            ):  # Non-GPE locations, mountain ranges, bodies of water.
                if "loc" in self.types:
                    self.results["LOC"].append(entity.text)
            elif (entity.label_ == "EVENT") and (
                entity.text not in self.results["EVENT"]
            ):  # Named hurricanes, battles, wars, sports events, etc.
                if "event" in self.types:
                    self.results["EVENT"].append(entity.text)
            elif (entity.label_ == "MONEY") and (
                entity.text not in self.results["MONEY"]
            ):  # Monetary values, including unit.
                if "money" in self.types:
                    self.results["MONEY"].append(entity.text)
        return self.results
