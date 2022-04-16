"""Fake data generator for testing"""
from iscc_registry.init import init

init()
import iscc_core as ic
import random
from blake3 import blake3
from iscc_registry.schema import Declaration


class Fake:
    def __init__(self):
        self.TIME = 1231002905
        self.BLOCK_HEIGHT = {i.name: i.value for i in ic.ST_ID}
        self.CHAIN_ID = 1
        self.rnd = random.Random(0)
        ic.Code.rgen = random.Random(0)

    @property
    def timestamp(self):
        self.TIME += self.rnd.randint(1, 1000)
        return self.TIME

    @property
    def iscc_id(self):
        return ic.Code.rnd(mt=ic.MT.ID).code

    @property
    def iscc_code(self):
        return ic.Code.rnd(mt=ic.MT.ISCC, bits=256).code

    @property
    def chain_id(self):
        self.CHAIN_ID = self.rnd.choice(list(ic.ST_ID)).value
        return self.CHAIN_ID

    @property
    def tx_idx(self):
        return self.rnd.randint(0, 3000)

    @property
    def tx_hash(self):
        bits = 32 * 8
        data = self.rnd.getrandbits(bits).to_bytes(length=bits // 8, byteorder="big")
        return "0x" + data.hex()

    @property
    def chain_name(self):
        return ic.ST_ID(self.CHAIN_ID).name

    @property
    def wallet(self):
        bits = 20 * 8
        data = self.rnd.getrandbits(bits).to_bytes(length=bits // 8, byteorder="big")
        return "0x" + data.hex()

    @property
    def block_hash(self):
        return "0x" + blake3(str(self.block_height).encode()).hexdigest()

    @property
    def block_height(self):
        self.BLOCK_HEIGHT[self.chain_name] += self.rnd.randint(1, 1000)
        return self.BLOCK_HEIGHT[self.chain_name]

    def rbytes(self, n: int):
        """Random bytes"""
        return self.rnd.getrandbits(n * 8).to_bytes(length=n, byteorder="big")

    @property
    def meta_url(self):
        base = "b"
        codec = b"\x01"
        ctype = b"\x55"
        htype = b"\x12"
        data = codec + ctype + htype + self.rbytes(32)
        cid = base + ic.encode_base32(data).lower()
        return f"ipfs://{cid}"

    @property
    def declaration(self):
        return Declaration(
            timestamp=self.timestamp,
            chain_id=self.chain_id,
            block_height=self.block_height,
            block_hash=self.block_hash,
            tx_idx=self.tx_idx,
            tx_hash=self.tx_hash,
            declarer=self.wallet,
            iscc_code=self.iscc_code,
            message=self.rnd.choice(
                ("frz:", "del:", None, None, None, None, None, None, None, None)
            ),
            meta_url=self.rnd.choice((None, self.meta_url)),
            registrar=self.rnd.choice((None, self.wallet)),
        )


def main():
    for x in range(1):
        dec = Fake().declaration
        dec.meta_url = "ipfs://bafkreiauxird7hexwesjlxfec57ecwaua7doqsodxzstixmhegrzulkjui"
        print(dec.json(indent=2))


if __name__ == "__main__":

    main()
    main()
