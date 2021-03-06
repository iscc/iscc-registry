import environ
from pathlib import Path


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "warning-todo-change-to-secure-secret-for-production-env"),
    DATABASE_URL=(str, "sqlite://:memory:"),
    REDIS_URL=(str, "redis://localhost:6379/?db=1"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CSRF_TRUSTED_ORIGINS=(list, ["http://localhost:8888"]),
    OBSERVER_TOKEN=(str, "observer-token"),
    IPFS_GATEWAY=(str, "https://opensea.mypinata.cloud/ipfs/"),
    CORS_ALLOW_ALL_ORIGINS=(bool, False),
    HUEY_SIMULATE=(bool, False),
    SENTRY_DSN=(str, ""),
    TESTNET=(bool, False),
    IPFS_RETRIES=(int, 10),
    IPFS_RETRY_DELAY=(int, 60),
    READ_TIMEOUT=(int, 30),
    SITE_EMAIL=(str, "example@example.com"),
)

SENTRY_DSN = env("SENTRY_DSN")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )


BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
INTERNAL_IPS = ["127.0.0.1"]
APPEND_SLASH = True

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
    "django_object_actions",
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
STATIC_ROOT = BASE_DIR / "static"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-admin-interface
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]
FIXTURE_DIRS = [BASE_DIR / "iscc_registry/fixtures"]

# huey background tasks
HUEY = {
    "name": "iscc_registry",
    "url": env("REDIS_URL"),
    "immediate_use_memory": env("HUEY_SIMULATE"),
    "immediate": env("HUEY_SIMULATE"),
}

# App Settings
IPFS_RETRIES = env("IPFS_RETRIES")
IPFS_RETRY_DELAY = env("IPFS_RETRY_DELAY")
OBSERVER_TOKEN = env("OBSERVER_TOKEN")
IPFS_GATEWAY = env("IPFS_GATEWAY")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS")
TESTNET = env("TESTNET")
READ_TIMEOUT = env("READ_TIMEOUT")
SITE_EMAIL = env("SITE_EMAIL")
