"""Initialize Django for standalone usage outside of WSGI context."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iscc_registry.settings")
django.setup()
