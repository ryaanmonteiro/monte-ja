"""Configurações do projeto Monte Já.

Segredos e banco de dados são lidos de variáveis de ambiente (nunca coloque
senhas reais neste arquivo, pois o repositório é público).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "chave-apenas-para-desenvolvimento-troque-em-producao")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "contas",
    "servicos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "montaja.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "servicos.context_processors.notificacoes",
            ],
        },
    },
]

WSGI_APPLICATION = "montaja.wsgi.application"

# Banco de dados: SQLite por padrão. Para PostgreSQL/MySQL defina DB_ENGINE=postgres|mysql
# e DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
_engine = os.environ.get("DB_ENGINE", "sqlite")
if _engine in ("postgres", "mysql"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql" if _engine == "postgres" else "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "montaja"),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432" if _engine == "postgres" else "3306"),
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_USER_MODEL = "contas.Usuario"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "contas:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Recuperação de senha: em desenvolvimento o e-mail aparece no terminal.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Sistema de moedas
CUSTO_DESBLOQUEIO_CONTATO = 1   # moedas gastas para ver o contato de um cliente
MOEDAS_BONUS_CADASTRO = 3       # moedas gratuitas ao cadastrar um montador
MOEDAS_PACOTE_SIMULADO = 5      # moedas adicionadas pela "compra" simulada
