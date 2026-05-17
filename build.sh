#!/usr/bin/env bash
# Build script para Render — corre durante o deploy.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_data
