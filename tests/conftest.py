import pytest
from iscc_registry import schema


@pytest.fixture
def dclr_a():
    return schema.Declaration(
        chain="ethereum",
        declarer="0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
        block_height=14514543,
        block_hash="0x60735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f05",
        tx_hash="0xcade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3a",
        timestamp=1649008119,
    )


@pytest.fixture
def dclr_a_update(dclr_a):
    new = dclr_a.copy()
    new.tx_hash = "0xcade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3b"
    new.meta_url = "ipfs://bafybeihcck6iocb2steuf4zwq53nfyce34xamke5za7gaq2qqoshmgab6u"
    return new
