import os
import json
import requests

REDIS_URL = os.environ["UPSTASH_REDIS_URL"]
REDIS_TOKEN = os.environ["UPSTASH_REDIS_TOKEN"]
KV_KEY = "known_releases"

HEADERS = {
    "Authorization": f"Bearer {REDIS_TOKEN}"
}

def get_known():
    r = requests.get(f"{REDIS_URL}/get/{KV_KEY}", headers=HEADERS)
    if r.status_code == 200:
        result = r.json().get("result")
        if result:
            return set(json.loads(result))
    return set()

def set_known(ids):
    payload = json.dumps(list(ids))
    r = requests.post(
        f"{REDIS_URL}/set/{KV_KEY}/{payload}",
        headers=HEADERS
    )
    return r.status_code == 200
