"""Load some demo data for testing."""
import iscc_registry.init
from iscc_registry import schema
from iscc_registry.transactions import register
from dev.fake import Fake


def load(n):
    for _ in range(n):
        obj = register(Fake.declaration)
        print(obj)


if __name__ == "__main__":
    load(1000)
