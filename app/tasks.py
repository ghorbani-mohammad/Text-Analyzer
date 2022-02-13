from __future__ import absolute_import, unicode_literals
import time
import pymongo, re
from tqdm import tqdm
import logging, datetime
from bson import ObjectId
from string import punctuation
from datetime import datetime as dt
from geopy.geocoders import Nominatim
from elasticsearch import Elasticsearch

from django.conf import settings
from django.db import transaction
from .celery import app
from analyzer.models import (
    News,
    Option,
    Operation,
    Keyword,
    Ner,
    Geo,
    Sentiment,
    Doc2vec,
    Related,
    NewsCategory,
    CategoryKeyword,
    ArmyCategory,
)
from analyzer.keyword import keywordAnalyzer
from analyzer.ner import ner
from analyzer.sentiment import sentimentAnalyzer
from analyzer.doc2vec import doc2vecAnalyzer
from analyzer.related import related
from analyzer.category import categoryx
from analyzer.summary import summaryx


logger = logging.getLogger('django')


@app.task(name='news_mongo_to_postgres')
def news_importer():
    myclient = pymongo.MongoClient(f"mongodb://mongodb:{settings.MONGO_DB_PORT}/")
    news_raw = myclient["news_raw"]["news_raw"]
    last_imported_news_id = Option.objects.get(key='last_imported_news').value
    print(f'last imported news mongo_id was {last_imported_news_id}')

    _filter = {"_id": {"$gt": ObjectId(last_imported_news_id)}, "body": {"$ne": ""}}
    projection = {
        'title': 1,
        'body': 1,
        'authors': 1,
        'source': 1,
        'authors': 1,
        'date': 1,
        'tags': 1,
        'link': 1,
        'agency_id': 1,
    }

    last_docs_count = news_raw.count_documents(_filter)
    print(f'{last_docs_count} number of documents are queued to insert to postgres')

    # Getting news that must be imported to postgres from mongo
    last_docs = news_raw.find(
        _filter, projection, no_cursor_timeout=True, sort=[('_id', pymongo.ASCENDING)]
    )

    for doc in last_docs[:10]:
        if News.objects.filter(_id=doc['_id']).count():
            continue
        print(f"to-> postgres.title is {doc['title']} and source is {doc['source']}")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            inserted_news = News.objects.create(
                _id=str(doc['_id']),
                title=doc['title'].strip(),
                body=doc['body'].strip(),
                source=doc['source'],
                date=dt.fromtimestamp(doc['date']),
                authors=doc['authors'],
                link=doc['link'],
                created_at=now,
                agency_id=doc['agency_id'],
            )
            Option.objects.filter(key='last_imported_news').update(
                value=str(doc['_id'])
            )
            Operation.objects.create(news_id=inserted_news)
            news_to_elastic.delay(delete=False, id=inserted_news.id)
    myclient.close()


@app.task(name='news_to_elastic')
def news_to_elastic(delete=False, id=None):
    address = f'http://elasticsearch:{settings.ELASTIC_DB_PORT}'
    es = Elasticsearch([address])
    index_name = 'elasticdb'
    if delete and es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    values = ('id', 'title', 'body', 'agency_id', 'source', 'date', '_id')
    if id:
        queryset = News.objects.filter(id=id)
    else:
        queryset = News.objects.order_by('-pk')
    batch_size = 10000
    step = 0
    total = queryset.count()
    while True:
        print(step * batch_size, min((step + 1) * batch_size, total))
        data = queryset[step * batch_size : min((step + 1) * batch_size, total)]
        data = data.values(*values)
        for item in data:
            item['date'] = datetime.datetime.timestamp(item['date'])
            item['mongo_id'] = item.pop('_id')
            es.index(index_name, body=item)
        if (step + 1) * batch_size >= total:
            break
        step += 1


def remove_htmls_tags_filter(text):
    return re.sub(re.compile('<.*?>'), '\n', text)


@app.task(name='news_keyword_extraction')
def news_keyword_extraction():
    keyword_extraction_limit = int(Option.objects.get(key='number_of_keywords').value)
    keyword_extraction_algo = Option.objects.get(
        key='keyword_extraction_algorithm'
    ).value

    news = Operation.objects.filter(keyword=False).order_by('-id')
    for item in news[:50]:
        with transaction.atomic():
            Keyword.objects.filter(news_id=item.news_id.id).delete()
            body = News.objects.get(id=item.news_id.id).body
            body = remove_htmls_tags_filter(body)
            keywords = keywordAnalyzer.analyzeKeyword(
                item.news_id.id, body, keyword_extraction_limit, keyword_extraction_algo
            )

            obj = []
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for keyword in keywords:
                obj.append(
                    Keyword(
                        news_id=item.news_id,
                        keyword=keyword,
                        created_at=now,
                        news_date=item.news_id.date,
                    )
                )
            Keyword.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(keyword=True)


@app.task(name='news_ner_extraction')
def news_ner_extraction():
    news = Operation.objects.filter(ner=False).order_by('-id')
    ner_extraction_types = (
        Option.objects.get(key='ner_extraction_types').value.replace(' ', '').split(',')
    )
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Ner.objects.filter(news_id=item.news_id.id).delete()
            news = News.objects.get(id=item.news_id.id)
            x = ner.NameEntityRecognition(
                item.news_id.id,
                remove_htmls_tags_filter(news.body),
                news.date,
                ner_extraction_types,
            )
            results = x.find_NER_tag(now)
            obj = []
            for entity in results.keys():
                for value in results.get(entity):
                    obj.append(
                        Ner(
                            news_id=item.news_id,
                            type=entity,
                            entity=value,
                            created_at=now,
                        )
                    )
            Ner.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(ner=True)


@app.task(name='news_geo_extraction')
def news_geo_extraction():
    use_google_geo = Option.objects.get(key='use_google_geo').value
    news = Operation.objects.filter(geo=False).order_by('-id')
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Geo.objects.filter(news_id=item.news_id.id).delete()
            gpes = Ner.objects.filter(type='GPE', news_id=item.news_id.id)
            obj = []
            for gpe in gpes:
                geo = (
                    Geo.objects.filter(location=gpe.entity)
                    .exclude(country=None)
                    .first()
                )
                if geo:
                    obj.append(
                        Geo(
                            news_id=item.news_id,
                            ner_id=gpe,
                            location=gpe.entity,
                            country=geo.country,
                            created_at=now,
                            news_date=item.news_id.date,
                        )
                    )
                else:
                    if use_google_geo == 'True':
                        proper_gpe.delay(gpe.id, 0)
            Geo.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(geo=True)


@app.task(name='gpe_to_geo')
def proper_gpe(gpe_id, number_of_try):
    gpe = Ner.objects.filter(id=gpe_id).first()
    location = gpe.entity
    number_of_try += 1
    if number_of_try == 3:
        print(f'can not resolve {location}')
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
            if result == 'United States of America':
                result = 'United States'
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            with transaction.atomic():
                Geo.objects.create(
                    news_id=gpe.news_id,
                    ner_id=gpe,
                    location=gpe.entity,
                    country=result,
                    created_at=now,
                    news_date=gpe.news_id.date,
                )
                Operation.objects.filter(news_id=gpe.news_id).update(geo=True)
            return 0
    except Exception as e:
        proper_gpe(gpe.id, number_of_try)


@app.task(name='news_sentiment')
def news_sentiment():
    sentiment_analyzer_algorithm = Option.objects.get(key='sentiment_analyzer').value
    news = Operation.objects.filter(sentiment=False).order_by('-id')
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Sentiment.objects.filter(news_id=item.news_id.id).delete()
            result = sentimentAnalyzer.analyzeSentiment(
                item.news_id.id,
                remove_htmls_tags_filter(item.news_id.body),
                now,
                sentiment_analyzer_algorithm,
            )
            Sentiment.objects.create(
                news_id=item.news_id,
                neg=round(result['neg'], 2),
                pos=round(result['pos'], 2),
                neu=round(result['neu'], 2),
                compound=round(result['compound'], 2),
                created_at=now,
            )
            Operation.objects.filter(news_id=item.news_id).update(sentiment=True)


@app.task(name='news_doc2vec')
def news_doc2vec():
    import spacy

    spacy_model = spacy.load("en_core_web_md")
    doc2vec_analyzer_algorithm = Option.objects.get(key='doc2vec_analyzer').value
    news = Operation.objects.filter(doc2vec=False).order_by('-id')
    for item in news[:50]:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            Doc2vec.objects.filter(news_id=item.news_id.id).delete()
            vector, vector_norm = doc2vecAnalyzer.analyzeDoc2vec(
                item.news_id.id,
                remove_htmls_tags_filter(item.news_id.body),
                now,
                doc2vec_analyzer_algorithm,
                spacy_model,
            )
            Doc2vec.objects.create(
                news_id=item.news_id,
                vector=vector,
                vector_norm=vector_norm,
                created_at=now,
            )
            Operation.objects.filter(news_id=item.news_id).update(doc2vec=True)


@app.task(name='news_related')
def news_related():
    related_extraction_limit = int(
        Option.objects.get(key='number_of_related_news').value
    )
    related_extraction_days = int(
        Option.objects.get(key='past_days_related_news').value
    )
    news = Operation.objects.filter(related_news=False, doc2vec=True).order_by('-id')
    for item in news[:20]:
        with transaction.atomic():
            Related.objects.filter(news_id=item.news_id.id).delete()
            results = related.relatedNews(
                item.news_id.id, related_extraction_limit, related_extraction_days
            )
            obj = []
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for x in results:
                obj.append(
                    Related(
                        news_id=item.news_id,
                        related_news_id=x['related_news_id'],
                        score=x['score'],
                        created_at=now,
                    )
                )
            Related.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(related_news=True)


@app.task(name='news_category')
def news_category():
    import spacy
    import numpy as np

    spacy_model = spacy.load("en_core_web_md")
    news = Operation.objects.filter(category=False).order_by('-id')
    categories = CategoryKeyword.objects.all()
    for item in news[:20]:
        results = categoryx.category(
            spacy_model, np, punctuation, item.news_id, categories
        )
        obj = []
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for x in results:
            obj.append(
                NewsCategory(
                    news_id=item.news_id,
                    army_category_id=ArmyCategory.objects.get(id=x),
                    score=results[x],
                    created_at=now,
                )
            )
        with transaction.atomic():
            NewsCategory.objects.filter(news_id=item.news_id.id).delete()
            NewsCategory.objects.bulk_create(obj)
            Operation.objects.filter(news_id=item.news_id).update(category=True)


@app.task(name='news_summary')
def news_summary():
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.summarizers.lsa import LsaSummarizer as Summarizer
    from sumy.utils import get_stop_words

    news = Operation.objects.filter(summary=False).order_by('-id')
    for item in news[:50]:
        if item.news_id.body is None or item.news_id.body == '':
            Operation.objects.filter(news_id=item.news_id).update(summary=True)
            continue
        result = summaryx.extractSummary(
            PlaintextParser,
            Tokenizer,
            Stemmer,
            Summarizer,
            get_stop_words,
            remove_htmls_tags_filter(item.news_id.body),
        )
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            if len(result):
                item.news_id.summary = result[0]
                item.news_id.updated_at = now
                item.news_id.save()
            Operation.objects.filter(news_id=item.news_id).update(summary=True)
