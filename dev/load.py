"""Load some demo data for testing."""
from iscc_registry import init

init.init()
from iscc_registry.transactions import register
from dev.fake import Fake


def load(n):
    objects = []
    f = Fake()
    for _ in range(n):
        obj = register(f.declaration)
        objects.append(obj)
    return objects


if __name__ == "__main__":

    load(10)
