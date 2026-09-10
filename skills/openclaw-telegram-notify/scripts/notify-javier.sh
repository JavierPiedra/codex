#!/usr/bin/env bash
set -euo pipefail

readonly TARGET_CHAT="434830632"
readonly FALLBACK_NODE="/Users/javierpiedra/.nvm/versions/node/v24.15.0/bin/node"
readonly FALLBACK_OPENCLAW="/Users/javierpiedra/.nvm/versions/node/v22.22.2/lib/node_modules/openclaw/openclaw.mjs"

if command -v openclaw >/dev/null 2>&1 && openclaw --version >/dev/null 2>&1; then
  exec openclaw message send --channel telegram --target "$TARGET_CHAT" "$@"
fi

if [[ -x "$FALLBACK_NODE" && -f "$FALLBACK_OPENCLAW" ]]; then
  exec "$FALLBACK_NODE" "$FALLBACK_OPENCLAW" message send \
    --channel telegram \
    --target "$TARGET_CHAT" \
    "$@"
fi

echo "OpenClaw is unavailable with a compatible Node runtime." >&2
exit 1
