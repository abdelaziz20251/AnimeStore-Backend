# config/settings.py
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Base & .env
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def str2bool(v: str, default=False) -> bool:
    if v is None:
        return default
    return str(v).lower() in ("true", "1", "yes", "y")

def split_and_clean(csv: str) -> list[str]:
    """
    Split comma-separated env values and clean:
    - strip spaces & quotes
    - remove http/https scheme
    - strip trailing slashes
    - drop empty items
    """
    if not csv:
        return []
    items = []
    for raw in csv.split(","):
        val = raw.strip().strip('"').strip("'")
        if not val:
            continue
        val = val.replace("https://", "").replace("http://", "")
        val = val.rstrip("/")
        if val:
            items.append(val)
    return items

def split_and_clean_origins(csv: str) -> list[str]:
    """
    Same as split_and_clean but KEEP scheme (required for CSRF origins),
    and just strip quotes/whitespace/trailing slashes.
    """
    if not csv:
        return []
    items = []
    for raw in csv.split(","):
        val = raw.strip().strip('"').strip("'").rstrip("/")
        if val:
            items.append(val)
    return items

# -----------------------------------------------------------------------------
# Core security flags
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-placeholder-key")
DEBUG = str2bool(os.getenv("DEBUG"), default=False)

# Hosts / CSRF from env (comma-separated)
# Railway provides RAILWAY_PUBLIC_DOMAIN and RAILWAY_STATIC_URL
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

if allowed_hosts_env:
    hosts = split_and_clean(allowed_hosts_env)
    ALLOWED_HOSTS = hosts if hosts else ["*"]
elif railway_domain:
    # allow exact domain and its subdomains
    ALLOWED_HOSTS = [railway_domain, f".{railway_domain}"]
elif not DEBUG:
    # safe default in production if not provided
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# CSRF Trusted Origins - include Railway domain if available
csrf_origins_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = split_and_clean_origins(csrf_origins_env)
elif railway_domain:
    CSRF_TRUSTED_ORIGINS = [f"https://{railway_domain}"]
else:
    CSRF_TRUSTED_ORIGINS = []

# When behind Railway's proxy (to make request.is_secure() True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "users.apps.UsersConfig",   # يجب أن يأتي قبل أي app يعتمد عليه
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "products.apps.ProductsConfig",
    "orders.apps.OrdersConfig",
    "sellers.apps.SellersConfig",
    "analytics.apps.AnalyticsConfig",
    "adminpanel.apps.AdminpanelConfig",
]

# Jazzmin (كما هو)
JAZZMIN_SETTINGS = {
    "site_title": "Dokkan",
    "site_header": "Zoz",
    "site_brand": "Library",
    "site_logo": "books/img/logo.png",
    "welcome_sign": "Welcome to the library",
    "copyright": "Reactors Team © 2025",
    "search_model": ["auth.User", "auth.Group"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"},
        {"app": "books"},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],
    "custom_links": {
        "books": [{
            "name": "Make Messages",
            "url": "make_messages",
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },
    "icons": {"auth": "fas fa-users-cog", "auth.user": "fas fa-user", "auth.Group": "fas fa-users"},
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
}

# -----------------------------------------------------------------------------
# Middleware / Templates / WSGI
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # مبكرًا
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static في الإنتاج
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------------------------------------------------------
# Database
#   - محلي: SQLite (افتراضي)
#   - Production: Postgres (Supabase) لو وفّرت DB_* في Railway
# -----------------------------------------------------------------------------
USE_DIRECT = str2bool(os.getenv("USE_DIRECT_DB"), default=False)

if os.getenv("DB_HOST"):
    if USE_DIRECT:
        DB_HOST = os.getenv("DIRECT_DB_HOST")
        DB_PORT = os.getenv("DIRECT_DB_PORT", "5432")
    else:
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "5432")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "OPTIONS": {"sslmode": "require", "connect_timeout": 10},
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("DB_PATH", BASE_DIR / "db.sqlite3"),
        }
    }

# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static & Media (WhiteNoise)
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        }
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", BASE_DIR / "media")

# -----------------------------------------------------------------------------
# DRF / JWT / Schema
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce API",
    "DESCRIPTION": "Full-stack e-commerce platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
cors_origins_env = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)
# keep scheme, strip quotes/trailing slashes
CORS_ALLOWED_ORIGINS = split_and_clean_origins(cors_origins_env)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type", "dnt", "origin",
    "user-agent", "x-csrftoken", "x-requested-with", "cache-control", "pragma", "expires",
]
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]

# -----------------------------------------------------------------------------
# Default PK
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
