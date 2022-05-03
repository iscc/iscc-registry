"""Background tasks"""
from huey.contrib import djhuey as huey
from iscc_registry.models import IsccId
from django.conf import settings
import requests
from loguru import logger as log


@huey.db_task(retries=settings.IPFS_RETRIES, delay=settings.IPFS_RETRY_DELAY)
def fetch_metadata(did: int):
    """Fetch and store ISCC metadata"""
    iscc_id_obj = IsccId.objects.get(did=did)
    log.debug(f"meta_url {iscc_id_obj.meta_url}")
    if not iscc_id_obj.meta_url:
        return
    if iscc_id_obj.meta_url.startswith("ipfs://"):
        url = settings.IPFS_GATEWAY + iscc_id_obj.meta_url.replace("ipfs://", "")
    else:
        url = iscc_id_obj.meta_url

    log.debug(f"fetch metadata from: {url}")
    meta = requests.get(url, timeout=settings.READ_TIMEOUT)
    data = meta.json()
    if data:
        log.info(f"fetched metadata for {iscc_id_obj.iscc_id}: {data}")
        iscc_id_obj.metadata = data
        iscc_id_obj.save()
