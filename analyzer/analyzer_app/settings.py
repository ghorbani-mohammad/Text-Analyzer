import os
import environ
from django.http.request import HttpRequest

env = environ.Env()

ALLOWED_HOSTS = ["*"]
MONGO_DB_PORT = "27017"
ELASTIC_DB_PORT = "9200"
DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
ELASTICSEARCH_DSL = {
    "default": {"hosts": "localhost:9200"},
}
DATABASES = {
    "default": {
        "HOST": "postgres",
        "NAME": "postgres",
        "USER": env.str("DB_USER"),
        "PORT": env.str("DB_PORT"),
        "PASSWORD": env.str("DB_PASS"),
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"options": "-c search_path=army"},
    },
}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "analyzer",
    "clear_cache",
    "corsheaders",
    "django_elasticsearch_dsl",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "analyzer_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "analyzer_app.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


USE_TZ = False
USE_I18N = True
USE_L10N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"


STATIC_URL = "/static/"


REST_FRAMEWORK = {
    # When you enable API versioning, the request.version attribute will contain a string
    # that corresponds to the version requested in the incoming client request.
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}


CORS_ORIGIN_ALLOW_ALL = True

# Celery
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["application/json"]
BROKER_URL = "redis://analyzer_redis:6379/10"
CELERY_RESULT_BACKEND = "redis://analyzer_redis:6379/10"

# monkey patch to get rid of message below in docker
# for bellow error (it happens because we have _ in container name)
# 'analyzer_api:80'. The domain name provided is not valid according to RFC 1034/1035.
HttpRequest.get_host = HttpRequest._get_raw_host
