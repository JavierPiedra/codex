#!/bin/sh
set -eu

if [ "$#" -ne 0 ]; then
  echo "run_report.sh does not accept arguments." >&2
  exit 64
fi

cd /Users/javierpiedra/Desktop/farcoyo
export POETRY_VIRTUALENVS_PATH="$PWD/.poetry-venvs"

exec poetry run python /Users/javierpiedra/.codex/automations/rappi-inveotry-upload-report/rappi_inventory_freshness_report.py --repo-root "$PWD"
