from analyzer.apps import AnalyzerConfig


class NameEntityRecognition:
    def __init__(self, text, types=None):
        self.text = text
        self.nlp = AnalyzerConfig.spacy_model
        self.types = types
        self.results = None

    @staticmethod
    def make_unique_list_result(result):
        for key in result.keys():
            result[key] = list(set(result[key]))
        return result

    def find_NER_tag(self):
        self.results = {
            "person": [],
            "FAC": [],
            "ORG": [],
            "GPE": [],
            "LOC": [],
            "EVENT": [],
            "MONEY": [],
        }
        doc = self.nlp(self.text)
        for entity in doc.ents:
            if entity.label_ == "PERSON":
                if "person" in self.types:
                    self.results["person"].append(entity.text)
            # Buildings, airports, highways, bridges, etc,
            elif entity.label_ == "FAC":
                if "fac" in self.types:
                    self.results["FAC"].append(entity.text)
            # Companies, agencies, institutions, etc.
            elif entity.label_ == "ORG":
                if "org" in self.types:
                    self.results["ORG"].append(entity.text)
            # Countries, cities, states.
            elif entity.label_ == "GPE":
                if "gpe" in self.types:
                    self.results["GPE"].append(entity.text)
            # Non-GPE locations, mountain ranges, bodies of water.
            elif entity.label_ == "LOC":
                if "loc" in self.types:
                    self.results["LOC"].append(entity.text)
            # Named hurricanes, battles, wars, sports events, etc.
            elif entity.label_ == "EVENT":
                if "event" in self.types:
                    self.results["EVENT"].append(entity.text)
            # Monetary values, including unit.
            elif entity.label_ == "MONEY":
                if "money" in self.types:
                    self.results["MONEY"].append(entity.text)
        self.results = NameEntityRecognition.make_unique_list_result(self.results)
        return self.results

    def find_all_tags(self):
        results = {
            "person": [],
            "FAC": [],
            "ORG": [],
            "GPE": [],
            "LOC": [],
            "EVENT": [],
            "MONEY": [],
        }
        doc = self.nlp(self.text)
        for entity in doc.ents:
            if entity.label_ == "PERSON":
                results["person"].append(entity.text)
            elif entity.label_ == "FAC":
                results["FAC"].append(entity.text)
            elif entity.label_ == "ORG":
                results["ORG"].append(entity.text)
            elif entity.label_ == "GPE":
                results["GPE"].append(entity.text)
            elif entity.label_ == "LOC":
                results["LOC"].append(entity.text)
            elif entity.label_ == "EVENT":
                results["EVENT"].append(entity.text)
            elif entity.label_ == "MONEY":
                results["MONEY"].append(entity.text)
        return NameEntityRecognition.make_unique_list_result(results)
