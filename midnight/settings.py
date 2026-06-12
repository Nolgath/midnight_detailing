"""
Django settings for midnight project — Midnight Detailing.
"""

from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_list(name, default=''):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-me-in-production',
)

DEBUG = _env_bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = _env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')

# Render injects its hostname as RENDER_EXTERNAL_HOSTNAME — add it automatically.
_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

CSRF_TRUSTED_ORIGINS = _env_list('DJANGO_CSRF_TRUSTED_ORIGINS', 'https://*.onrender.com')

# Segurança em produção — o Render termina o TLS no proxy.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 dias; subir após validar HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'midnight.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'midnight.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization — Portuguese (Portugal)
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']


# Static & media
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email — console backend in dev, SMTP via env vars in prod
EMAIL_BACKEND = os.getenv(
    'DJANGO_EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = _env_bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = _env_bool('EMAIL_USE_SSL', default=False)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@midnightdetailing.pt')

# Destination for contact form / quote requests
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'geral@midnightdetailing.pt')

# Destination for booking requests (cart -> Marcar e concluir)
BOOKING_EMAIL = os.getenv('BOOKING_EMAIL', 'mddetailing2026@gmail.com')


# Site / business info (used in templates via context processor)
SITE_NAME = 'Midnight Detailing'
SITE_TAGLINE = 'Detalhe automóvel e lavagem de carros premium em Alverca do Ribatejo'

# URL pública do site — usada em canonical, Open Graph, sitemap e JSON-LD.
# Em produção no Render, RENDER_EXTERNAL_URL é definido automaticamente.
SITE_URL = os.getenv(
    'SITE_URL',
    os.getenv('RENDER_EXTERNAL_URL', 'http://127.0.0.1:8000'),
).rstrip('/')

# Contactos do negócio — expostos a todos os templates via context processor.
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '+351900000000')
BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '+351900000000')

# Localização / SEO local (foco: Alverca do Ribatejo)
BUSINESS_LOCALITY = os.getenv('BUSINESS_LOCALITY', 'Alverca do Ribatejo')
BUSINESS_REGION = os.getenv('BUSINESS_REGION', 'Lisboa')
BUSINESS_POSTAL_CODE = os.getenv('BUSINESS_POSTAL_CODE', '2615')

# Redes sociais / presença online — só aparecem no site quando definidas.
GOOGLE_BUSINESS_URL = os.getenv(
    'GOOGLE_BUSINESS_URL', 'https://share.google/WTt0SSLsVUKHG4ySR',
)
INSTAGRAM_URL = os.getenv(
    'INSTAGRAM_URL', 'https://www.instagram.com/midnight.detailing.oficial/',
)
FACEBOOK_URL = os.getenv('FACEBOOK_URL', '')
TIKTOK_URL = os.getenv(
    'TIKTOK_URL', 'https://www.tiktok.com/@midnight.detailin8',
)

# Nº de reviews na ficha Google. Quando definido, o JSON-LD inclui
# aggregateRating 5.0 com este número de avaliações.
GOOGLE_REVIEW_COUNT = os.getenv('GOOGLE_REVIEW_COUNT', '')
