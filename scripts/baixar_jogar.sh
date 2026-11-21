#!/usr/bin/env bash
set -euo pipefail

REPO="SoloLF17/first-RPG-test"
BASE_URL="https://github.com/$REPO/releases/latest/download"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/duelo-veyrion"
ARCHIVE="/tmp/duelo-veyrion-linux-x64.tar.gz"

command -v curl >/dev/null || { echo "Erro: curl não está instalado." >&2; exit 1; }
rm -f "$ARCHIVE"
mkdir -p "$INSTALL_DIR"
curl -fL "$BASE_URL/duelo-veyrion-linux-x64.tar.gz" -o "$ARCHIVE"
tar -xzf "$ARCHIVE" -C "$INSTALL_DIR" --strip-components=1
exec "$INSTALL_DIR/DueloDeVeyrion"
