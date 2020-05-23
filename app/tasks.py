from __future__ import absolute_import, unicode_literals
import requests
import logging, datetime, redis, requests, json

import time
import pymongo, re
from bson import ObjectId
from django.db import transaction
from datetime import datetime as dt
from geopy.geocoders import Nominatim

from .celery import app
from celery import current_app
from analyzer.models import News, Option, Operation, Keyword, Ner, Geo, Sentiment, Doc2vec
from analyzer.keyword import keywordAnalyzer
from analyzer.ner import ner
from analyzer.sentiment import sentimentAnalyzer
from analyzer.doc2vec import doc2vecAnalyzer


logger = logging.getLogger('django')

@app.task(name='news_mongo_to_postgres')
def news_importer():
    myclient = pymongo.MongoClient("mongodb://138.201.77.42:27017/")
    news_raw = myclient["news_raw"]["news_raw"]
    last_imported_news_id = Option.objects.get(key='last_imported_news').value
    print('last imported news mongo_id was {}'.format(last_imported_news_id))
    

    _filter = {
                "_id": {"$gt": ObjectId(last_imported_news_id)},
                "body":{"$ne": ""}
            }
    projection = {
                'title': 1, 'body': 1, 'authors' :1,
                'source': 1, 'authors': 1, 'date': 1,
                'tags': 1, 'link':1, 'agency_id':1,
            }

    last_docs_count = news_raw.count_documents(_filter)
    print('{} number of documents are queued to insert to postgres'.format(last_docs_count))

    # Getting news that must be imported to postgres from mongo
    last_docs = news_raw.find(_filter, projection, no_cursor_timeout=True, sort= [('_id', pymongo.ASCENDING)])

    for doc in last_docs[:10]:
        if News.objects.filter(_id=doc['_id']).count():
            continue
        
        # filters on body
        doc['body'] = re.sub(re.compile('<.*?>'), '\n', doc['body'])

        print("importing to postgres. doc title is '{}' and source is '{}' ".format(doc['title'], doc['source']))
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with transaction.atomic():
            inserted_news = News.objects.create(
                _id=str(doc['_id']),
                title=doc['title'].strip(), 
                body=doc['body'].strip(), 
                source=doc['source'], 
                date= dt.fromtimestamp(doc['date']),
                authors= doc['authors'],
                link=doc['link'],
                created_at= now,
                agency_id= doc['agency_id'],
            )
            Option.objects.filter(key='last_imported_news').update(value=str(doc['_id']))
            Operation.objects.create(
                news_id = inserted_news
            )

    myclient.close()


@app.task(name='news_keyword_extraction')
def news_keyword_extraction():
    keyword_extraction_limit = int(Option.objects.get(key='number_of_keywords').value)
    keyword_extraction_algo = Option.objects.get(key='keyword_extraction_algorithm').value

    news = Operation.objects.filter(keyword=False)
    for item in news[:50]:
        with transaction.atomic():
            Keyword.objects.filter(news_id=item.news_id.id).delete()
            body = News.objects.get(id=item.news_id.id).body
            keywords = keywordAnalyzer.analyzeKeyword(item.news_id.id, body, keyword_extraction_limit, keyword_extraction_algo)
            
            obj = []
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for keyword in keywords:
                obj.append(Keyword(news_id=item.news_id, keyword=keyword, created_at=now))
            Keyword.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(keyword=True)


@app.task(name='news_ner_extraction')
def news_ner_extraction():
    news = Operation.objects.filter(ner=False)
    ner_extraction_types = Option.objects.get(key='ner_extraction_types').value.replace(' ', '').split(',')
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Ner.objects.filter(news_id=item.news_id.id).delete()
            news = News.objects.get(id=item.news_id.id)
            x = ner.NameEntityRecognition(item.news_id.id, news.body, news.date, ner_extraction_types)
            results = x.find_NER_tag(now)
            obj = []
            for entity in results.keys():
                for value in results.get(entity):
                    obj.append(Ner(news_id=item.news_id, type=entity, entity=value, created_at=now))
            Ner.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(ner=True)


@app.task(name='news_geo_extraction')
def news_geo_extraction():
    news = Operation.objects.filter(geo=False)
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Geo.objects.filter(news_id=item.news_id.id).delete()
            gpes = Ner.objects.filter(type='GPE', news_id=item.news_id.id)
            obj = []
            for gpe in gpes:
                geo = Geo.objects.filter(location=gpe.entity).exclude(country=None).first()
                if geo:
                    obj.append(Geo(news_id=item.news_id, ner_id=gpe, location=gpe.entity, country=geo.country, created_at=now, news_date=item.news_id.date))
                else:
                    proper_gpe.delay(gpe.id, 0)
            Geo.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(geo=True)



@app.task(name='gpe_to_geo')
def proper_gpe(gpe_id, number_of_try):
    gpe = Ner.objects.filter(id=gpe_id).first()
    location = gpe.entity
    number_of_try += 1
    if number_of_try == 10:
        print('can not resolve {}'.format(location))
        return 0
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
            proper_gpe(gpe.id, number_of_try)
        else:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            with transaction.atomic():
                Geo.objects.create(news_id=gpe.news_id, ner_id=gpe, location=gpe.entity, country=result, created_at=now, news_date=gpe.news_id.date)
                Operation.objects.filter(news_id=gpe.news_id).update(geo=True)
            return 0
    except Exception as e:
        proper_gpe(gpe.id, number_of_try)


@app.task(name='news_sentiment')
def news_sentiment():
    sentiment_analyzer_algorithm = Option.objects.get(key='sentiment_analyzer').value
    news = Operation.objects.filter(sentiment=False)
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Sentiment.objects.filter(news_id=item.news_id.id).delete()
            result = sentimentAnalyzer.analyzeSentiment(item.news_id.id, item.news_id.body, now, sentiment_analyzer_algorithm)
            Sentiment.objects.create(news_id=item.news_id,  neg=round(result['neg'], 2), pos=round(result['pos'], 2), neu=round(result['neu'], 2), compound=round(result['compound'], 2), created_at= now)
            Operation.objects.filter(news_id=item.news_id).update(sentiment=True)


@app.task(name='news_doc2vec')
def news_doc2vec():
    doc2vec_analyzer_algorithm = Option.objects.get(key='doc2vec_analyzer').value
    news = Operation.objects.filter(doc2vec=False)
    print(news.count())
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Doc2vec.objects.filter(news_id=item.news_id.id).delete()
            vector, vector_norm = doc2vecAnalyzer.analyzeDoc2vec(item.news_id.id, item.news_id.body, now, doc2vec_analyzer_algorithm)
            Doc2vec.objects.create(news_id=item.news_id, vector=vector, vector_norm=vector_norm, created_at=now)
            Operation.objects.filter(news_id=item.news_id).update(doc2vec=True)

