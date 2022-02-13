# Generated by Django 3.0.5 on 2020-05-20 04:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=70)),
                ('source', models.CharField(max_length=70)),
                ('agency_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'news',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField()),
                ('keyword', models.BooleanField(default=False)),
                ('ner', models.BooleanField(default=False)),
                ('category', models.BooleanField(default=False)),
                ('sentiment', models.BooleanField(default=False)),
                ('doc2vec', models.BooleanField(default=False)),
                ('related_news', models.BooleanField(default=False)),
                ('news_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', related_query_name='operation', to='analyzer.News')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]