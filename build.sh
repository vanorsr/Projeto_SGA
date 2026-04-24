#!/usr/bin/env bash
# build.sh - Script de build executado pelo Render em cada deploy

# Abort no primeiro erro
set -o errexit

echo "==> Instalando dependências..."
pip install -r requirements.txt

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

echo "==> Aplicando migrations..."
python manage.py migrate

echo "==> Build concluído com sucesso!"
