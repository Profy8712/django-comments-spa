from .base import *

# --------------------------------------------------
# Production
# --------------------------------------------------
DEBUG = False

# Use domain-based hosts (no IP default)
ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "comments-spa-test.duckdns.org,localhost,127.0.0.1,comments_backend,comments_frontend",
)

# If you are behind nginx reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Let nginx handle http->https redirect (you already do 80 -> 443)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", False)

# Cookies should be secure in HTTPS production
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", True)

# Optional: security hardening (safe defaults)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "same-origin"

# Elasticsearch switch (AWS ресурсов мало)
ELASTICSEARCH_ENABLED = env_bool("ELASTICSEARCH_ENABLED", False)
