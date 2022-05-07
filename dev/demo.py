"""Initialize a fresh installation (resets pre-existing development database).

- creates the database
- import theme fixtures
- create initial user

"""
import sys

from loguru import logger as log
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iscc_registry.settings")
from django.contrib.auth import get_user_model
from django.core import management
import django
import pathlib


HERE = pathlib.Path(__file__).parent.absolute()
django.setup()


def delete_dev_db():
    dev_db = HERE / "dev.db"
    if dev_db.exists():
        log.info(f"purge dev database at {dev_db}")
        try:
            os.remove(HERE / "dev.db")
        except Exception:
            log.error(f"failed deleting dev database - retry after stopping dev server")
            sys.exit(0)


def migrate():
    log.info("run database migrations")
    management.call_command("migrate")


def load_fixtures():
    log.info("load theme fixture")
    management.call_command("loaddata", "--app", "admin_interface.Theme", "theme")
    log.info("load chains fixture")
    management.call_command("loaddata", "--app", "iscc_registry.ChainModel", "chains")


def collect_static():
    log.info("collect staticfiles")
    management.call_command("collectstatic", "--noinput")


def create_user():
    from django.conf import settings
    import secrets

    log.info("create initial user")
    if settings.DEBUG:
        username = "demo"
        password = "demo"
        email = "demo@eexample.com"
    else:
        username = "admin"
        password = secrets.token_hex(32)
        email = settings.SITE_EMAIL

    User = get_user_model()

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        log.info("############ CREATED INITIAL SUPERUSER ############ ")
        log.info(f"Username: {username}")
        log.info(f"Password: {password}")
    else:
        log.info("Skipped creating initial user - already exists")


def demo():
    delete_dev_db()
    migrate()
    load_fixtures()
    collect_static()
    create_user()


if __name__ == "__main__":
    demo()
