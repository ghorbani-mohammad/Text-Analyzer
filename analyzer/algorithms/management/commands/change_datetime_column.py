from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Change type of datetime column from with timezone to without timezone'
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''ALTER TABLE ner_country ALTER COLUMN news_date TYPE "timestamp"''')