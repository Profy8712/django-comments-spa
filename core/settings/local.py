# core/settings/local.py
from .base import *
import os
import urllib.request

DEBUG = True

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# Local usually without HTTPS proxy
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# -----------------------------------------------------------------------------
# Elasticsearch (local)
# -----------------------------------------------------------------------------
# Controls:
#   ELASTICSEARCH_ENABLED=1|0
#   ELASTICSEARCH_HOST=http://elasticsearch:9200
#   ELASTICSEARCH_DSL_AUTOSYNC=1|0
#   ELASTICSEARCH_REQUIRED=1|0
#
ELASTICSEARCH_ENABLED = env_bool("ELASTICSEARCH_ENABLED", "1")
ELASTICSEARCH_DSL_AUTOSYNC = env_bool("ELASTICSEARCH_DSL_AUTOSYNC", "1")
ELASTICSEARCH_REQUIRED = env_bool("ELASTICSEARCH_REQUIRED", "0")

ELASTICSEARCH_HOST = os.getenv(
    "ELASTICSEARCH_HOST",
    "http://elasticsearch:9200",
)

def _es_reachable(host: str) -> bool:
    try:
        urllib.request.urlopen(host, timeout=1.0).read()
        return True
    except Exception:
        return False

if ELASTICSEARCH_ENABLED:
    ES_OK = _es_reachable(ELASTICSEARCH_HOST)

    if not ES_OK and ELASTICSEARCH_REQUIRED:
        raise RuntimeError(
            f"Elasticsearch is required but not reachable: {ELASTICSEARCH_HOST}. "
            f"Start it with: docker compose --profile search up -d"
        )

    ELASTICSEARCH_DSL = {
        "default": {
            "hosts": ELASTICSEARCH_HOST,
        }
    }

    # Prevent crashes on save if ES is temporarily down
    if not ES_OK:
        ELASTICSEARCH_DSL_AUTOSYNC = False
else:
    ELASTICSEARCH_DSL_AUTOSYNC = False
    ELASTICSEARCH_DSL = {
        "default": {
            "hosts": "http://127.0.0.1:9200",
        }
    }
