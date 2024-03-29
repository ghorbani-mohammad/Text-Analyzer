from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField


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
    summary = models.TextField()
    source = models.CharField(max_length=70)
    agency_id = models.BigIntegerField()
    date = models.DateTimeField()
    link = models.CharField(max_length=250)
    created_at = models.DateTimeField()
    authors = ArrayField(models.CharField(max_length=70))

    class Meta:
        managed = False
        db_table = "news"

    def __str__(self):
        return f"{self.pk} - {self.title}"


class Operation(BaseModel):
    news_id = models.OneToOneField(
        "News",
        related_name="operations",
        related_query_name="operation",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    keyword = models.BooleanField(default=False)
    ner = models.BooleanField(default=False)
    category = models.BooleanField(default=False)
    sentiment = models.BooleanField(default=False)
    doc2vec = models.BooleanField(default=False)
    related_news = models.BooleanField(default=False)
    geo = models.BooleanField(default=False)
    summary = models.BooleanField(default=False)

    def __str__(self):
        return f"({self.pk} - {self.news_id})"


class Option(models.Model):
    key = models.CharField(max_length=70)
    value = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "options"

    def __str__(self):
        return f"{self.key}"


class Keyword(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="keywords",
        related_query_name="keyword",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    keyword = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    news_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "news_keyword"

    def __str__(self):
        return f"({self.pk} - {self.news_id} - {self.keyword})"


class Ner(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="ners",
        related_query_name="ner",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    entity = models.CharField(max_length=70)
    type = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "news_ner"

    def __str__(self):
        return f"({self.pk} - {self.news_id} - {self.entity})"


class Geo(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="geos",
        related_query_name="geo",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    ner_id = models.OneToOneField(
        "Ner",
        related_name="geos",
        related_query_name="geo",
        on_delete=models.CASCADE,
        db_column="ner_id",
    )
    location = models.CharField(max_length=70)
    country = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    news_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "ner_country"

    def __str__(self):
        return f"({self.pk} - {self.news_id} - {self.location})"


class Sentiment(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="sentiments",
        related_query_name="sentiment",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    neg = models.FloatField(default=0.0)
    pos = models.FloatField(default=0.0)
    neu = models.FloatField(default=0.0)
    compound = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "news_sentiment"

    def __str__(self):
        return f"{self.pk}"


class Doc2vec(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="doc2vecs",
        related_query_name="doc2vec",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    vector = JSONField()
    vector_norm = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "news_vector"

    def __str__(self):
        return f"{self.pk}"


class Related(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="relateds",
        related_query_name="related",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    related_news_id = models.BigIntegerField()
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "news_related"

    def __str__(self):
        return f"{self.pk}"


class ArmyCategory(models.Model):
    label = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "army_category"


class ArmyKeyword(models.Model):
    label = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "army_keyword"


class CategoryKeyword(models.Model):
    army_category_id = models.OneToOneField(
        "ArmyCategory",
        related_name="categorykeywords",
        related_query_name="categorykeyword",
        on_delete=models.CASCADE,
        db_column="army_category_id",
    )
    army_keyword_id = models.OneToOneField(
        "ArmyKeyword",
        related_name="keywords",
        related_query_name="keyword",
        on_delete=models.CASCADE,
        db_column="army_keyword_id",
    )

    class Meta:
        managed = False
        db_table = "category_keyword"


class NewsCategory(models.Model):
    news_id = models.OneToOneField(
        "News",
        related_name="news",
        related_query_name="news",
        on_delete=models.CASCADE,
        db_column="news_id",
    )
    army_category_id = models.OneToOneField(
        "ArmyCategory",
        related_name="newscategories",
        related_query_name="newscategory",
        on_delete=models.CASCADE,
        db_column="army_category_id",
    )
    score = models.FloatField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "news_category"
