import pytest
from iscc_registry import schema

from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "--app", "iscc_registry.ChainModel", "chains")


@pytest.fixture
def dclr_a():
    return schema.Declaration(
        timestamp=1649008119,
        chain_id=2,
        block_height=14514543,
        block_hash="0x60735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f05",
        tx_idx=0,
        tx_hash="0xcade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3a",
        declarer="0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
    )


@pytest.fixture
def dclr_a_update():
    return schema.Declaration(
        timestamp=1649008120,
        chain_id=2,
        block_height=14514543,
        block_hash="0x60735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f06",
        tx_idx=1,
        tx_hash="0xcade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3b",
        declarer="0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
        meta_url="ipfs://bafybeihcck6iocb2steuf4zwq53nfyce34xamke5za7gaq2qqoshmgab6u",
    )
