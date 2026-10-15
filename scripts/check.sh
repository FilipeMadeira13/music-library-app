#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Um segredo efêmero serve apenas às verificações; não é gravado em .env.
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-$(python -c 'import secrets; print(secrets.token_urlsafe(64))')}"
export DJANGO_SETTINGS_MODULE=config.settings
install -d -m 700 var var/backups var/static

python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m mypy
python manage.py check
python manage.py makemigrations --check --dry-run
python -m coverage erase
python -m coverage run manage.py test --verbosity 2
python manage.py collectstatic --noinput
python -m coverage run scripts/smoke.py
python -m coverage combine
python -m coverage report
python -m coverage xml
python -m coverage html
python scripts/diagnostics.py
