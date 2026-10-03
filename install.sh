#!/usr/bin/env bash
# Instala el asesor de viajes en Claude Code (~/.claude).
# Uso: ./install.sh [--force]   (--force sobrescribe una instalación previa del paquete; nunca toca tu KB personal)
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
FORCE="${1:-}"

mkdir -p "$DEST/agents" "$DEST/skills"

if [[ -e "$DEST/skills/viajes" || -e "$DEST/agents/asesor-viajes.md" ]] && [[ "$FORCE" != "--force" ]]; then
  echo "Ya existe una instalación en $DEST (agents/asesor-viajes.md o skills/viajes)."
  echo "Para actualizarla: ./install.sh --force   (tu KB personal en agents/_kb/viajes no se toca)"
  exit 1
fi

cp "$SRC/agents/asesor-viajes.md" "$DEST/agents/asesor-viajes.md"
mkdir -p "$DEST/skills/viajes"
cp -R "$SRC/skills/viajes/." "$DEST/skills/viajes/"
chmod +x "$DEST/skills/viajes/scripts/travel.py"

# Crea la KB personal vacía y su .env si no existen (no sobrescribe nada)
VIAJES_KB="${VIAJES_KB:-$DEST/agents/_kb/viajes}" python3 "$DEST/skills/viajes/scripts/travel.py" setup >/dev/null

echo "✅ Asesor de viajes instalado en $DEST"
echo "   KB personal: $DEST/agents/_kb/viajes/  (privada, no la compartas)"
echo "   Siguiente: abre Claude Code y pídele ayuda con un viaje."
echo "   Claves opcionales: python3 $DEST/skills/viajes/scripts/travel.py status"
