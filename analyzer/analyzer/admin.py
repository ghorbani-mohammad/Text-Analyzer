from django.contrib import admin

from . import models


@admin.register(models.Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "news_id",
        "keyword",
        "ner",
        "category",
        "sentiment",
        "doc2vec",
        "related_news",
        "geo",
        "summary",
        "created_at",
    )
    list_per_page = 30
    raw_id_fields = ("news_id",)
