import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from twilio.rest import Client
from vercel_kv import kv

ARTIST_ID = "69eRfY40RjSFrZOToECdiS"
KV_KEY = "known_releases"

def handler(request):
    # Spotify
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.environ["SPOTIFY_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
        )
    )

    # Twilio
    twilio = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    known = set(kv.get(KV_KEY) or [])

    results = sp.artist_albums(
        ARTIST_ID,
        album_type="album,single",
        limit=50
    )

    current = set()
    alerts = []

    for album in results["items"]:
        album_id = album["id"]
        current.add(album_id)

        if album_id not in known:
            alerts.append(
                f"🚨 *NEW SPOTIFY RELEASE*\n\n"
                f"{album['name']}\n"
                f"{album['release_date']}\n\n"
                f"{album['external_urls']['spotify']}"
            )

    if alerts:
        for msg in alerts:
            twilio.messages.create(
                from_="whatsapp:+14155238886",
                to=os.environ["TO_WHATSAPP"],
                body=msg
            )

    kv.set(KV_KEY, list(current))

    return {
        "statusCode": 200,
        "body": json.dumps({"alerts_sent": len(alerts)})
    }
