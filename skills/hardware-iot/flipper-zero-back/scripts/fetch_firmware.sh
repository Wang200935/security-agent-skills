#!/bin/bash
# Fetch latest official Flipper Zero firmware .tgz and .dfu
# Usage: ./fetch_firmware.sh [output_dir] [channel]
#   output_dir: defaults to current dir
#   channel: release (default) | release-candidate | development
#
# Pre-requisites: curl, python3
# Works without a connected Flipper — useful as pre-backup step.

set -euo pipefail

OUT_DIR="${1:-.}"
CHANNEL="${2:-release}"
MANIFEST_URL="https://update.flipperzero.one/firmware/directory.json"

mkdir -p "$OUT_DIR"

# ⚠️  DO NOT use update.flipperzero.one/qFlipper/directory.json
#  That URL is for the qFlipper APP, not the Flipper Zero firmware.

echo "📥 Fetching firmware manifest for channel: $CHANNEL"
echo "   URL: $MANIFEST_URL"

# GET (not HEAD — server returns 405 for HEAD)
curl -sL "$MANIFEST_URL" -o /tmp/flipper_fw_dir.json

# Parse with Python
read VERSION TGZ_URL DFU_URL < <(python3 -c "
import json
with open('/tmp/flipper_fw_dir.json') as f:
    d = json.load(f)
for ch in d['channels']:
    if ch['id'] == '$CHANNEL':
        v = ch['versions'][0]
        tgz = dfu = ''
        for f in v['files']:
            if f['target'] == 'f7' and f['type'] == 'update_tgz':
                tgz = f['url']
            elif f['target'] == 'f7' and f['type'] == 'full_dfu':
                dfu = f['url']
        print(v['version'], tgz, dfu)
        break
")

if [ -z "$VERSION" ]; then
    echo "❌ Channel '$CHANNEL' not found"
    exit 1
fi

echo "✅ Found release: $VERSION"
echo "   Update .tgz: $TGZ_URL"
echo "   Full .dfu:  $DFU_URL"
echo ""

# Download
echo "📦 Downloading update .tgz..."
curl -sL "$TGZ_URL" -o "$OUT_DIR/flipper-z-f7-update-$VERSION.tgz"
echo "   ✅ $(ls -lh "$OUT_DIR/flipper-z-f7-update-$VERSION.tgz" | awk '{print $5}')"

echo "📦 Downloading full .dfu (for DFU recovery)..."
curl -sL "$DFU_URL" -o "$OUT_DIR/flipper-z-f7-full-$VERSION.dfu"
echo "   ✅ $(ls -lh "$OUT_DIR/flipper-z-f7-full-$VERSION.dfu" | awk '{print $5}')"

# SHA256 verify
echo ""
echo "🔐 SHA256 checksums:"
echo "   .tgz: $(shasum -a 256 "$OUT_DIR/flipper-z-f7-update-$VERSION.tgz" | cut -d' ' -f1)"
echo "   .dfu: $(shasum -a 256 "$OUT_DIR/flipper-z-f7-full-$VERSION.dfu" | cut -d' ' -f1)"

echo ""
echo "✅ Done. Files in: $OUT_DIR"
ls -lh "$OUT_DIR"/flipper-z-f7-*.$VERSION.* 2>/dev/null
