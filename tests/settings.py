import os

os.environ["DATABASE_URL"] = "sqlite:///./dev/test.db"
os.environ["SECRET_KEY"] = "test-secret"
from iscc_registry.settings import *
