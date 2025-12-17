from .base import *

DEBUG = False


ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "44.220.53.72")

# У тебя HTTPS через nginx self-signed, поэтому доверяем заголовкам прокси
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", "0")

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", "0")
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", "0")

# AWS: Elasticsearch выключен из-за ресурсов
ELASTICSEARCH_ENABLED = env_bool("ELASTICSEARCH_ENABLED", "0")
