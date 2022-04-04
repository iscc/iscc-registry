"""Background tasks"""
from huey import crontab
from loguru import logger as log
from huey.contrib import djhuey as huey


@huey.db_periodic_task(crontab(minute="*/1"))
def example_task():
    log.info("running example task")
