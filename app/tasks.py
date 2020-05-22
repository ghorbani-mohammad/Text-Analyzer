from __future__ import absolute_import, unicode_literals
import requests
import logging, datetime, redis, requests, json

import time
import pymongo, re
from bson import ObjectId
from django.db import transaction
from datetime import datetime as dt

from .celery import app
from celery import current_app
from analyzer.models import News, Option, Operation, Keyword
from analyzer.keyword import keywordAnalyzer


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
    for item in news:
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
