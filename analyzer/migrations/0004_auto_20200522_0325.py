# Generated by Django 3.0.5 on 2020-05-22 03:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0003_auto_20200522_0320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='news_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', related_query_name='operation', to='analyzer.News', unique=True),
        ),
    ]
