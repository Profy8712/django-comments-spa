from .base import *

DEBUG = True

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["localhost","127.0.0.1"])

# Local обычно без HTTPS-прокси
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Локально можно держать Elasticsearch включенным
# (если в docker-compose локальном есть elasticsearch + django_elasticsearch_dsl в requirements)
ELASTICSEARCH_ENABLED = env_bool("ELASTICSEARCH_ENABLED", "1")
