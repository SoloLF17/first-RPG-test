#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install -r requirements.txt pyinstaller
rm -rf build dist

pyinstaller \
  --noconfirm \
  --clean \
  --onedir \
  --name DueloDeVeyrion \
  --add-data "jogo/assets:jogo/assets" \
  jogo/__main__.py

cp LICENSE "dist/DueloDeVeyrion/"
tar -czf "dist/duelo-veyrion-linux-x64.tar.gz" -C dist DueloDeVeyrion
echo "Arquivo gerado: dist/duelo-veyrion-linux-x64.tar.gz"
