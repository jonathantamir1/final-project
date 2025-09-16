# statuspage/statuspage/configuration.py
import os

def env_list(name: str, default: str) -> list[str]:
    """Split comma-separated env var into a clean list."""
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]

#
# Required Settings
#

# Hostnames allowed to access the app (first is preferred). Use commas for multiple.
# Example: ALLOWED_HOSTS="status.example.com,status.internal"
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "*")

# PostgreSQL database configuration.
DATABASE = {
    "NAME": os.getenv("DB_NAME", "status-page"),
    "USER": os.getenv("DB_USER", "statuspage"),
    "PASSWORD": os.getenv("DB_PASSWORD", "changeme"),
    # For local VM use 'localhost'; in Docker Compose you'll pass DB_HOST=db via env.
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", ""),
    "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "300")),
}

# Redis configuration (tasks queue + caching).
REDIS_TASKS_HOST = os.getenv("REDIS_TASKS_HOST", "localhost")  # in Docker: 'redis'
REDIS_CACHING_HOST = os.getenv("REDIS_CACHING_HOST", "localhost")

REDIS = {
    "tasks": {
        "HOST": REDIS_TASKS_HOST,
        "PORT": int(os.getenv("REDIS_TASKS_PORT", "6379")),
        "PASSWORD": os.getenv("REDIS_TASKS_PASSWORD", ""),
        "DATABASE": int(os.getenv("REDIS_TASKS_DB", "0")),
        "SSL": False,
        # 'INSECURE_SKIP_TLS_VERIFY': False,
    },
    "caching": {
        "HOST": REDIS_CACHING_HOST,
        "PORT": int(os.getenv("REDIS_CACHING_PORT", "6379")),
        "PASSWORD": os.getenv("REDIS_CACHING_PASSWORD", ""),
        "DATABASE": int(os.getenv("REDIS_CACHING_DB", "1")),
        "SSL": False,
        # 'INSECURE_SKIP_TLS_VERIFY': False,
    },
}

# Public site URL (used e.g. in emails)
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# SECRET_KEY must be long and random in production. Prefer passing via env.
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PROD")

#
# Optional Settings
#

ADMINS = [
    # ("John Doe", "jdoe@example.com"),
]

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    #     "OPTIONS": {"min_length": 10},
    # },
]

# If app is served under a subpath, e.g. https://example.com/status-page/
BASE_PATH = os.getenv("BASE_PATH", "")

# CORS settings
CORS_ORIGIN_ALLOW_ALL = os.getenv("CORS_ORIGIN_ALLOW_ALL", "False").lower() == "true"
CORS_ORIGIN_WHITELIST = []  # e.g. ["https://hostname.example.com"]
CORS_ORIGIN_REGEX_WHITELIST = []  # e.g. [r"^(https?://)?(\w+\.)?example\.com$"]

# Debug flag (NEVER enable in production)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Email settings
EMAIL = {
    "SERVER": os.getenv("EMAIL_SERVER", "localhost"),
    "PORT": int(os.getenv("EMAIL_PORT", "25")),
    "USERNAME": os.getenv("EMAIL_USERNAME", ""),
    "PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
    "USE_SSL": os.getenv("EMAIL_USE_SSL", "False").lower() == "true",
    "USE_TLS": os.getenv("EMAIL_USE_TLS", "False").lower() == "true",
    "TIMEOUT": int(os.getenv("EMAIL_TIMEOUT", "10")),
    "FROM_EMAIL": os.getenv("EMAIL_FROM", ""),
}

INTERNAL_IPS = ("127.0.0.1", "::1")

LOGGING = {}  # Provide Django LOGGING dict if needed

# Login session lifetime (seconds). None -> Django default (14 days)
LOGIN_TIMEOUT = None

# MEDIA_ROOT = "/opt/status-page/statuspage/media"  # Uncomment to override upload path

FIELD_CHOICES = {}

PLUGINS = [
    # "sp_uptimerobot",
    # "sp_external_status_providers",
]

PLUGINS_CONFIG = {
    "sp_uptimerobot": {
        "uptime_robot_api_key": os.getenv("UPTIMEROBOT_API_KEY", ""),
    },
}

# RQ / Queues (django-rq)
RQ_DEFAULT_TIMEOUT = int(os.getenv("RQ_DEFAULT_TIMEOUT", "300"))

# Build a Redis URL for django-rq from the 'tasks' config above
_pwd = os.getenv("REDIS_TASKS_PASSWORD", "")
_pwd = f":{_pwd}@" if _pwd else ""
REDIS_URL = f"redis://{_pwd}{REDIS['tasks']['HOST']}:{REDIS['tasks']['PORT']}/{REDIS['tasks']['DATABASE']}"

RQ_QUEUES = {
    "default": {"URL": REDIS_URL}
}

# Cookies
CSRF_COOKIE_NAME = os.getenv("CSRF_COOKIE_NAME", "csrftoken")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "sessionid")

# Time zone & formats
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")

DATE_FORMAT = "N j, Y"
SHORT_DATE_FORMAT = "Y-m-d"
TIME_FORMAT = "g:i a"
SHORT_TIME_FORMAT = "H:i:s"
DATETIME_FORMAT = "N j, Y g:i a"
SHORT_DATETIME_FORMAT = "Y-m-d H:i"
