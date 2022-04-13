import environ
from pathlib import Path


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "warning-todo-change-to-secure-secret-for-production-env"),
    DATABASE_URL=(str, "sqlite://:memory:"),
    REDIS_URL=(str, "redis://localhost:6379/?db=1"),
    ALLOWED_HOSTS=(list, ["*"]),
    OBSERVER_TOKEN=(str, "observer-token"),
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

AUTH_USER_MODEL = "iscc_registry.User"

INSTALLED_APPS = [
    "colorfield",
    "public_admin",
    "admin_interface",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_json_widget",
    "huey.contrib.djhuey",
    "iscc_registry",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "iscc_registry.urls"

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

WSGI_APPLICATION = "iscc_registry.wsgi.application"


DATABASES = {
    "default": env.db(),
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "iscc_registry/static"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-admin-interface
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]
FIXTURE_DIRS = [BASE_DIR / "iscc_registry/fixtures"]

# huey background tasks
HUEY = {
    "name": "iscc_registry",
    "url": env("REDIS_URL"),
    "immediate_use_memory": env("DEBUG"),
    "immediate": env("DEBUG"),
}

# Access token for observers
OBSERVER_TOKEN = env("OBSERVER_TOKEN")
