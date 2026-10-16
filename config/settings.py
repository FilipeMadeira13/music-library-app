"""Configuração explícita do monólito local; variáveis recebidas do ambiente."""

import os
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / "var" / "static"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY com um segredo aleatório de 50+ caracteres."
    )

_debug = os.environ.get("DJANGO_DEBUG", "false").lower()
if _debug not in {"true", "false"}:
    raise ImproperlyConfigured("DJANGO_DEBUG deve ser true ou false.")
DEBUG = _debug == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS or any("*" in host or host.startswith(".") for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS exige hosts específicos, sem curingas.")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
for _origin in CSRF_TRUSTED_ORIGINS:
    _parsed = urlsplit(_origin)
    if (
        _parsed.scheme not in {"http", "https"}
        or not _parsed.hostname
        or _parsed.username is not None
        or _parsed.password is not None
        or _parsed.path
        or _parsed.query
        or _parsed.fragment
        or "*" in _origin
        or _parsed.hostname.startswith(".")
    ):
        raise ImproperlyConfigured(
            "Use origens CSRF HTTP/HTTPS específicas, sem caminho ou curinga."
        )

INSTALLED_APPS = ["django.contrib.staticfiles", "library.apps.LibraryConfig"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": ["django.template.context_processors.request"],
        },
    },
]

_database_path = os.environ.get("LIBRARY_DATABASE_PATH", "")
if _database_path and not Path(_database_path).is_absolute():
    raise ImproperlyConfigured("LIBRARY_DATABASE_PATH deve ser um caminho absoluto local.")
_database_location = (
    Path(_database_path) if _database_path else BASE_DIR / "var" / "library.sqlite3"
)
if _database_location.is_relative_to(STATIC_ROOT) or _database_location.resolve().is_relative_to(
    STATIC_ROOT.resolve()
):
    raise ImproperlyConfigured("LIBRARY_DATABASE_PATH deve ficar fora dos arquivos estáticos.")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _database_location,
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 3},
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "pt-br"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "America/Fortaleza")
try:
    ZoneInfo(TIME_ZONE)
except (ValueError, ZoneInfoNotFoundError) as exc:
    raise ImproperlyConfigured("DJANGO_TIME_ZONE deve ser um fuso IANA válido.") from exc
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = False
WHITENOISE_AUTOREFRESH = False
DATA_UPLOAD_MAX_MEMORY_SIZE = 256 * 1024
