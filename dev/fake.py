"""Fake data generator for testing"""
import iscc_core as ic
import random
from blake3 import blake3


random.seed(1)


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
    def time(cls):
        cls.TIME += random.randint(1, 1000)
        return cls.TIME

    @classproperty
    def iscc_id(cls):
        return ic.Code.rnd(mt=ic.MT.ID)

    @classproperty
    def iscc_code(cls):
        return ic.Code.rnd(mt=ic.MT.ISCC, bits=256)

    @classproperty
    def chain_id(cls):
        cls.CHAIN_ID = random.choice(list(ic.ST_ID)).value
        return cls.CHAIN_ID

    @classproperty
    def chain_name(cls):
        return ic.ST_ID(cls.CHAIN_ID).name

    @classproperty
    def wallet(cls):
        bits = 20 * 8
        data = random.getrandbits(bits).to_bytes(length=bits // 8, byteorder="big")
        return "0x" + data.hex()

    @classproperty
    def block_hash(cls):
        bits = 30 * 8
        return "0x" + blake3(str(cls.block_height).encode()).hexdigest()

    @classproperty
    def block_height(cls):
        cls.BLOCK_HEIGHT[cls.chain_name] += random.randint(1, 1000)
        return cls.BLOCK_HEIGHT[cls.chain_name]


def main():
    print(Fake.time)
    print(Fake.iscc_id)
    print(Fake.iscc_code)
    print(Fake.chain_name)
    print(Fake.chain_id)
    print(Fake.wallet)
    print(Fake.block_hash)
    print(Fake.block_height)


if __name__ == "__main__":
    main()
