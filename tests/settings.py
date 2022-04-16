import os

os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["SECRET_KEY"] = "test-secret"
from iscc_registry.settings import *

HUEY = {
    "immediate_use_memory": True,
    "immediate": True,
}
