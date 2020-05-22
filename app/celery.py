from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# TODO: redis port and ip and db must be dynamic
app = Celery('app',
             broker='redis://analyzer_redis:6379/10',
             backend='redis://analyzer_redis:6379/10',
             include=['app.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=7200,
)

app.conf.beat_schedule = {
    'news_mongo_to_postgres': {
        'task': 'news_mongo_to_postgres',
        'schedule': 1 * 20,
    },
}

if __name__ == '__main__':
    app.start()
