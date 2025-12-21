from .base import *

# -----------------------------------------------------------------------------
# Production settings
# -----------------------------------------------------------------------------

DEBUG = False

# Must be set in .env.prod (domain/IP)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "")

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Usually handled by Nginx (80 -> 443)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", "0")

# HTTPS cookies
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", "1")
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", "1")

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# Disable Elasticsearch by default in prod (small instances)
ELASTICSEARCH_ENABLED = env_bool("ELASTICSEARCH_ENABLED", "0")
