#!/bin/bash
# capture_drphub.sh
# Usage: capture_drphub.sh /path/to/input.html /path/to/output.png WIDTH HEIGHT
set -euo pipefail
IN_HTML="$1"
OUT_PNG="$2"
WIDTH="${3:-1280}"
HEIGHT="${4:-800}"

# Try headless chromium
if command -v chromium >/dev/null 2>&1; then
  chromium --headless --disable-gpu --screenshot="$OUT_PNG" --window-size=${WIDTH},${HEIGHT} "file://$IN_HTML"
  echo "Captured with chromium: $OUT_PNG"
  exit 0
fi

# Fallback to wkhtmltoimage
if command -v wkhtmltoimage >/dev/null 2>&1; then
  wkhtmltoimage --quality 90 --width $WIDTH --height $HEIGHT "$IN_HTML" "$OUT_PNG"
  echo "Captured with wkhtmltoimage: $OUT_PNG"
  exit 0
fi

echo "No capture tool found (chromium or wkhtmltoimage)." >&2
exit 2
