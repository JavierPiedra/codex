"""Check native dependencies without reading credentials or user data."""
import importlib.util
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parent.parent
path = root / "plugins/javier/skills/invoice-goodancestor/scripts/wakatime_client_hours.py"
spec = importlib.util.spec_from_file_location("wakatime_runtime", path)
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
backend = client.native_keyring()
path = root / "plugins/javier/skills/exa-deep-search/scripts/exa_deep_search.py"
spec = importlib.util.spec_from_file_location("exa_runtime", path)
exa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exa)
exa_backend = exa.native_keyring()
exa.search("Offline runtime validation", dry_run=True)
ZoneInfo("America/Mexico_City")
print(json.dumps({"python": sys.version.split()[0], "platform": sys.platform,
                  "credential_backend": type(backend).__module__ + "." + type(backend).__name__,
                  "exa_credential_backend": type(exa_backend).__module__ + "." + type(exa_backend).__name__,
                  "exa_request_validation": True}))
