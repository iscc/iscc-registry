#!/usr/bin/env bash
set -euo pipefail

echo "--> starting huey"
poetry run python manage.py run_huey
