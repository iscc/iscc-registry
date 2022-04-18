"""Background tasks"""
from huey import crontab
from huey.contrib import djhuey as huey
from iscc_registry.models import IsccIdModel
from django.conf import settings
import requests
from loguru import logger as log


@huey.db_periodic_task(crontab(minute="*/1"))
def example_task():
    log.info("running example task")


@huey.db_task()
def fetch_metadata(did: int):
    """Fetch and store ISCC metadata"""
    iscc_id_obj = IsccIdModel.objects.get(did=did)
    log.debug(f"meta_url {iscc_id_obj.meta_url}")
    if not iscc_id_obj.meta_url:
        return
    if iscc_id_obj.meta_url.startswith("ipfs://"):
        url = settings.IPFS_GATEWAY + iscc_id_obj.meta_url.lstrip("ipfs://")
    else:
        url = iscc_id_obj.meta_url

    log.debug(f"fetch metadata from: {url}")
    try:
        meta = requests.get(url, timeout=10)
        data = meta.json()
        if data:
            log.info(f"fetched metadata for {iscc_id_obj.iscc_id}: {data}")
            iscc_id_obj.metadata = data
            iscc_id_obj.save()
    except Exception as e:
        log.error(e)
