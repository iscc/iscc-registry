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
        log.info(f"purge dev database at {dev_db}")
        try:
            os.remove(HERE / "dev.db")
        except Exception:
            log.error(f"failed deleting dev database - retry after stopping dev server")
            sys.exit(0)

    log.info("purge existing migrations")
    migrations_path = HERE.parent / "iscc_registry/migrations"
    migrations_files = migrations_path.glob("000*.py")
    for mig in migrations_files:
        log.info(f"purging {mig.name}")
        os.remove(mig)

    log.info("run database migrations")
    management.call_command("migrate")

    log.info("load fixtures")
    management.call_command("loaddata", "--app", "admin_interface.Theme", "theme")
    management.call_command("loaddata", "--app", "iscc_registry.ChainModel", "chains")

    log.info("collect staticfiles")
    management.call_command("collectstatic", "--noinput")

    log.info("create demo user")
    User = get_user_model()
    username = "demo"
    password = "demo"
    email = "demo@eexample.com"
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        log.info("############ CREATED DEMO SUPERUSER ############ ")
        log.info(f"Username: {username}")
        log.info(f"Password: {password}")
    else:
        log.info("Skipped creating demo user - already exists")


if __name__ == "__main__":
    demo()
