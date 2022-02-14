from sklearn.metrics.pairwise import cosine_similarity
import dateutil.relativedelta
import datetime

from analyzer.models import Doc2vec


def relatedNews(news_id, limit, days):
    temp = []

    # Retrieve news vector
    news_vect = Doc2vec.objects.filter(news_id=news_id).first().vector
    # convert from string to array
    news_vect = news_vect.strip("][").split(", ")

    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    x = datetime.date.today() - datetime.timedelta(days)

    candids = Doc2vec.objects.filter(created_at__gte=x)

    for news in candids:
        # convert from string to array
        news_id = news.news_id.id
        news = news.vector.strip("][").split(", ")
        score = cosine_similarity([news], [news_vect])[0][0]
        temp.append((news_id, score))

    related_news = sorted(temp, key=lambda tup: tup[1], reverse=True)
    related_news = related_news[1 : min(limit, len(candids))]

    if len(related_news) == 0:
        return

    result = []
    for news in related_news:
        result.append(dict(news_id=news_id, related_news_id=news[0], score=news[1]))
    return result
