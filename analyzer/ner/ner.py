import spacy
import time
from geopy.geocoders import Nominatim
from datetime import datetime as dt

class NameEntityRecognition():
    def __init__(self, news_id, news_body, news_date, types):
        self.news_body = news_body
        self.news_id = news_id
        self.news_date = news_date
        self.nlp = spacy.load("en_core_web_sm")
        self.types = types
        self.results = None
        # self.find_NER_tag(now)

    def find_NER_tag(self, now):
        # try:
        self.results = {'person': [], 'FAC': [], 'ORG': [], 'GPE': [], 'LOC': [], 'EVENT': [], 'MONEY': []}
        doc = self.nlp(self.news_body)
        for entity in doc.ents:
            if (entity.label_ == 'PERSON') and (entity.text not in self.results['person']):
                if 'person' in self.types:
                    self.results['person'].append(entity.text)
            elif (entity.label_ == "FAC") and (entity.text not in self.results['FAC']):  # Buildings, airports, highways, bridges, etc,
                if 'fac' in self.types:
                    self.results['FAC'].append(entity.text)
            elif (entity.label_ == 'ORG') and (entity.text not in self.results['ORG']):  # Companies, agencies, institutions, etc.
                if 'org' in self.types:
                    self.results['ORG'].append(entity.text)
            elif (entity.label_ == 'GPE') and (entity.text not in self.results['GPE']):  # Countries, cities, states.
                if 'gpe' in self.types:
                    self.results['GPE'].append(entity.text)
            elif (entity.label_ == 'LOC') and (entity.text not in self.results['LOC']):  # Non-GPE locations, mountain ranges, bodies of water.
                if 'loc' in self.types:
                    self.results['LOC'].append(entity.text)
            elif (entity.label_ == 'EVENT') and (entity.text not in self.results['EVENT']):  # Named hurricanes, battles, wars, sports events, etc.
                if 'event' in self.types:
                    self.results['EVENT'].append(entity.text)
            elif (entity.label_ == 'MONEY') and (entity.text not in self.results['MONEY']):  # Monetary values, including unit.
                if 'money' in self.types:
                    self.results['MONEY'].append(entity.text)
        # print(self.results)
        return self.results
            # print(self.results)
            # for entity in results.keys():
            #     for value in results.get(entity):
            #         query = db.insert(news_ner).values(news_id=self.news_id, type=entity, entity=value, created_at= now) 
            #         ner_result_id = connection.execute(query).inserted_primary_key[0]
            #         if entity == 'GPE':
            #             self.country(ner_result_id, self.news_id, value)
        # except Exception as e:
        #     print(e)
    def get_results(self):
        print(self.results)
        return self.results

    def proper_gpe(self, location, number_of_try):
        number_of_try += 1
        if number_of_try == 10:
            return 'can not resolve {}'.format(location)
        try:
            geolocator = Nominatim(user_agent='hemmat')
            find_location = geolocator.geocode(location, language='en')
            loc_details = find_location.raw['display_name'].split(',')
            result = None
            if len(loc_details) < 2:
                result = loc_details[0].strip()
            if len(loc_details) >= 2:
                result = loc_details[-1:][0].strip()
            if result is None:
                self.proper_gpe(location, number_of_try)
            else:
                return result
        except Exception as e:
            self.proper_gpe(location, number_of_try)


    def country(self, ner_id, news_id, location):
        select_st = ner_country.select().where(ner_country.c.location == location)
        temp = list(connection.execute(select_st))
        if len(temp) == 0:
            result = self.proper_gpe(location, 0)
            if result == 'United States of America':
                result = 'United States'
        else:
            result = temp[0]['country'] 
        query = db.insert(ner_country).values(
                ner_id=ner_id,
                news_id=news_id,
                location=location,
                country=result,
                created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                news_date= dt.fromtimestamp(self.news_date)
                )
        connection.execute(query)


