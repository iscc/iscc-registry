from django.db import migrations
from django.core.management import call_command


def load_theme(apps, schema_editor):
    call_command("loaddata", "--app", "admin_interface.Theme", "theme")


class Migration(migrations.Migration):

    dependencies = [
        ("iscc_registry", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_theme),
    ]
