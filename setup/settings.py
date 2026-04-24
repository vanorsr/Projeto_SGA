"""
Django settings for setup project.
Configurado para funcionar em DEV (local, SQLite) e PROD (Render, PostgreSQL).
"""
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SEGURANÇA E AMBIENTE
# ============================================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Render define RENDER_EXTERNAL_HOSTNAME automaticamente
RENDER_HOST = os.getenv('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# Domínios customizados podem ser adicionados via env var (separados por vírgula)
# Exemplo: EXTRA_HOSTS=sga.meudominio.com.br,www.sga.meudominio.com.br
extra_hosts = os.getenv('EXTRA_HOSTS', '')
if extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in extra_hosts.split(',') if h.strip()])

# CSRF precisa conhecer os domínios que vão enviar POST
CSRF_TRUSTED_ORIGINS = []
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_HOST}')
if extra_hosts:
    for h in extra_hosts.split(','):
        h = h.strip()
        if h:
            CSRF_TRUSTED_ORIGINS.append(f'https://{h}')


# ============================================================================
# APPS E MIDDLEWARE
# ============================================================================
INSTALLED_APPS = [
    "core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve estáticos em prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "setup.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "setup.wsgi.application"


# ============================================================================
# DATABASE
# Lê DATABASE_URL do ambiente. Se não existir, cai em SQLite local (dev).
# ============================================================================
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Produção (Supabase/PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Desenvolvimento local (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================================
# LOCALIZAÇÃO
# ============================================================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ============================================================================
# ARQUIVOS ESTÁTICOS (CSS, JS, imagens)
# ============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # onde collectstatic agrupa tudo
STATICFILES_DIRS = []

# WhiteNoise com compressão e hash nos nomes (cache agressivo)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================================
# SEGURANÇA EM PRODUÇÃO
# ============================================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# ============================================================================
# OUTROS
# ============================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================================
# CHAVES DE IA
# ============================================================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# ============================================================================
# AUTENTICAÇÃO — URLs de redirect
# ============================================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'