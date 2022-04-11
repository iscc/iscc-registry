"""Fake data generator for testing"""
import iscc_registry.init
import iscc_core as ic
import random
from blake3 import blake3
from iscc_registry.schema import Declaration
from iscc_registry.transactions import register


rnd = random.Random(0)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class Fake:

    TIME = 1231002905
    BLOCK_HEIGHT = {i.name: i.value for i in ic.ST_ID}
    CHAIN_ID = 1

    @classproperty
    def timestamp(cls):
        cls.TIME += rnd.randint(1, 1000)
        return cls.TIME

    @classproperty
    def iscc_id(cls):
        return ic.Code.rnd(mt=ic.MT.ID).code

    @classproperty
    def iscc_code(cls):
        return ic.Code.rnd(mt=ic.MT.ISCC, bits=256).code

    @classproperty
    def chain_id(cls):
        cls.CHAIN_ID = rnd.choice(list(ic.ST_ID)).value
        return cls.CHAIN_ID

    @classproperty
    def tx_idx(cls):
        return rnd.randint(0, 3000)

    @classproperty
    def tx_hash(cls):
        bits = 32 * 8
        data = rnd.getrandbits(bits).to_bytes(length=bits // 8, byteorder="big")
        return "0x" + data.hex()

    @classproperty
    def chain_name(cls):
        return ic.ST_ID(cls.CHAIN_ID).name

    @classproperty
    def wallet(cls):
        bits = 20 * 8
        data = rnd.getrandbits(bits).to_bytes(length=bits // 8, byteorder="big")
        return "0x" + data.hex()

    @classproperty
    def block_hash(cls):
        return "0x" + blake3(str(cls.block_height).encode()).hexdigest()

    @classproperty
    def block_height(cls):
        cls.BLOCK_HEIGHT[cls.chain_name] += rnd.randint(1, 1000)
        return cls.BLOCK_HEIGHT[cls.chain_name]

    @staticmethod
    def rbytes(n: int):
        """Random bytes"""
        return rnd.getrandbits(n * 8).to_bytes(length=n, byteorder="big")

    @classproperty
    def meta_url(cls):
        base = "b"
        codec = b"\x01"
        ctype = b"\x55"
        htype = b"\x12"
        data = codec + ctype + htype + cls.rbytes(32)
        cid = base + ic.encode_base32(data).lower()
        return f"ipfs://{cid}"

    @classproperty
    def declaration(cls):
        return Declaration(
            timestamp=cls.timestamp,
            chain_id=cls.chain_id,
            block_height=cls.block_height,
            block_hash=cls.block_hash,
            tx_idx=cls.tx_idx,
            tx_hash=cls.tx_hash,
            declarer=cls.wallet,
            iscc_code=cls.iscc_code,
            message=rnd.choice(("frz:", "del:", None, None, None, None, None, None, None, None)),
            meta_url=rnd.choice((None, cls.meta_url)),
            registrar=rnd.choice((None, cls.wallet)),
        )


def main():
    from pprint import pp

    for x in range(10):
        pp(Fake.declaration.dict())


def load(n):
    for x in range(n):
        register(Fake.declaration)


if __name__ == "__main__":
    load(1000)
