#!/usr/bin/env bash
# Build phase no Render: só dependências + static (não tem acesso à DB em free plan).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
