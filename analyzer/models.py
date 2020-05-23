from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        abstract = True


class News(models.Model):
    _id = models.CharField(max_length=70)
    title = models.CharField(max_length=70)
    body = models.TextField()
    source = models.CharField(max_length=70)
    agency_id = models.BigIntegerField()
    date = models.DateTimeField()
    link = models.CharField(max_length=250)
    created_at = models.DateTimeField()
    authors = ArrayField(models.CharField(max_length=70))
    
    class Meta:
       managed = False
       db_table = 'news'
    
    def __str__(self):
        return '{}. {}'.format(self.id, self.title)

class Operation(BaseModel):
    news_id = models.OneToOneField('News', related_name='operations', related_query_name='operation',
                                 on_delete=models.CASCADE, db_column='news_id')
    keyword = models.BooleanField(default=False)
    ner = models.BooleanField(default=False)
    category = models.BooleanField(default=False)
    sentiment = models.BooleanField(default=False)
    doc2vec = models.BooleanField(default=False)
    related_news = models.BooleanField(default=False)
    geo = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.id)


class Option(models.Model):
    key = models.CharField(max_length=70)
    value = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'options'
    
    def __str__(self):
        return '{}'.format(self.key)
    

class Keyword(models.Model):
    news_id = models.OneToOneField('News', related_name='keywords', related_query_name='keyword',
                                 on_delete=models.CASCADE, db_column='news_id')
    keyword = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'news_keyword'
    
    def __str__(self):
        return '{}'.format(self.id)


class Ner(models.Model):
    news_id = models.OneToOneField('News', related_name='ners', related_query_name='ner',
                                 on_delete=models.CASCADE, db_column='news_id')
    entity = models.CharField(max_length=70)
    type = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'news_ner'
    
    def __str__(self):
        return '{}'.format(self.id)


class Geo(models.Model):
    news_id = models.OneToOneField('News', related_name='geos', related_query_name='geo',
                                 on_delete=models.CASCADE, db_column='news_id')
    ner_id = models.OneToOneField('Ner', related_name='geos', related_query_name='geo',
                                 on_delete=models.CASCADE, db_column='ner_id')
    location = models.CharField(max_length=70)
    country = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    news_date = models.DateTimeField()

    class Meta:
       managed = False
       db_table = 'ner_country'
    
    def __str__(self):
        return '{}'.format(self.id)
                        

class Sentiment(models.Model):
    news_id = models.OneToOneField('News', related_name='sentiments', related_query_name='sentiment',
                                 on_delete=models.CASCADE, db_column='news_id')
    neg = models.FloatField(default=0.0)
    pos = models.FloatField(default=0.0)
    neu = models.FloatField(default=0.0)
    compound = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'news_sentiment'
    
    def __str__(self):
        return '{}'.format(self.id)