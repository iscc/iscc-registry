"""Load some demo data for testing."""
import iscc_registry.init
from iscc_registry import schema
from iscc_registry.transactions import register


def load():
    a = schema.Declaration(
        timestamp=1649008119,
        chain_id=2,
        block_height=14514543,
        block_hash="0xaa735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f05",
        tx_idx=0,
        tx_hash="0xaade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3a",
        declarer="0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
    )
    iscc_id_obj_a = register(a)

    b = schema.Declaration(
        timestamp=1649009000,
        chain_id=2,
        block_height=14514544,
        block_hash="0xbb735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f06",
        tx_idx=0,
        tx_hash="0xbbde12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3b",
        declarer="0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
        meta_url="ipfs://bafybeihcck6iocb2steuf4zwq53nfyce34xamke5za7gaq2qqoshmgab6u",
    )
    iscc_id_obj_b = register(b)

    c = schema.Declaration(
        timestamp=1649009900,
        chain_id=2,
        block_height=14514544,
        block_hash="0xbb735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f06",
        tx_idx=0,
        tx_hash="0xccde12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3b",
        declarer="0x1bd91ee08f21be3de0ba2ba6918e714da6b45836",
        iscc_code="KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
    )

    iscc_id_obj_c = register(c)

    print(iscc_id_obj_a)
    print(iscc_id_obj_b)
    print(iscc_id_obj_c)


if __name__ == "__main__":
    load()
