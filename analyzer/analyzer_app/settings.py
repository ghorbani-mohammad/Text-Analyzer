import os
import environ

env = environ.Env()

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "n6ld+$-+#x(j7!vys)uvbscvsmm51nwn+(z#3zeqjx+a-!vt_@"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_IP = env.str("SERVER_IP")
DB_PORT = env.str("DB_PORT")
DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
ELASTIC_DB_PORT = "9200"
MONGO_DB_PORT = "27017"
ELASTICSEARCH_DSL = {
    "default": {"hosts": "localhost:9200"},
}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"options": "-c search_path=army"},
        "NAME": "postgres",
        "USER": DB_USER,
        "PASSWORD": DB_PASS,
        "HOST": "postgres",
        "PORT": DB_PORT,
    },
}


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "algorithm",
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


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"


REST_FRAMEWORK = {
    # When you enable API versioning, the request.version attribute will contain a string
    # that corresponds to the version requested in the incoming client request.
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}


CORS_ORIGIN_ALLOW_ALL = True

# Celery
BROKER_URL = "redis://analyzer_redis:6379/10"
CELERY_RESULT_BACKEND = "redis://analyzer_redis:6379/10"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"
