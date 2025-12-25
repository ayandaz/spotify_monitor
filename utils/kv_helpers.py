import os
import json
import requests

KV_BASE = "https://kv.vercel.io/v1/kv"
KV_KEY = "known_releases"
KV_TOKEN = os.environ.get("VERCEL_KV_TOKEN")  # Add in Vercel environment variables

def get_known():
    """Retrieve known album IDs from Vercel KV."""
    headers = {"Authorization": f"Bearer {KV_TOKEN}"}
    r = requests.get(f"{KV_BASE}/{KV_KEY}", headers=headers)
    if r.status_code == 200:
        return set(json.loads(r.text))
    return set()

def set_known(ids):
    """Update known album IDs in Vercel KV."""
    headers = {
        "Authorization": f"Bearer {KV_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.put(f"{KV_BASE}/{KV_KEY}", headers=headers, data=json.dumps(list(ids)))
    return r.status_code == 200
