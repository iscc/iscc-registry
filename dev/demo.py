"""Initialize a fresh installation (resets pre-existing development database).

- creates the database
- import theme fixtures
- create demo user

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


def demo():
    dev_db = HERE / "dev.db"
    if dev_db.exists():
        log.info(f"deleting dev database at {dev_db}")
        try:
            os.remove(HERE / "dev.db")
        except Exception:
            log.error(f"failed deleting dev database - retry after stopping dev server")
            sys.exit(0)
    log.info("applying database migrations")
    management.call_command("makemigrations")
    management.call_command("migrate")

    log.info("creating demo user")
    User = get_user_model()
    username = "demo"
    password = "demo"
    email = "demo@eexample.com"
    User.objects.create_superuser(username=username, password=password, email=email)
    log.info(f"Username: {username}")
    log.info(f"Password: {password}")


if __name__ == "__main__":
    demo()
