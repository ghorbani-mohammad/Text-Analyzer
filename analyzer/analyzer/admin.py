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


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "key", "created_at", "updated_at")
