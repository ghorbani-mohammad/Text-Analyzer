# Generated by Django 3.0.5 on 2020-05-22 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0007_auto_20200522_1402'),
    ]

    operations = [
        migrations.CreateModel(
            name='NER',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', models.CharField(max_length=70)),
                ('type', models.CharField(max_length=70)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'news_ner',
                'managed': False,
            },
        ),
    ]
