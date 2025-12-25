import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from twilio.rest import Client
from utils.kv_helpers import get_known  # import from utils

ARTIST_ID = os.environ.get("SPOTIFY_ARTIST_ID")

def handler(request):
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.environ["SPOTIFY_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
        )
    )

    twilio = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    known = get_known()

    results = sp.artist_albums(
        ARTIST_ID,
        album_type="album,single",
        limit=50
    )

    alerts = []

    for album in results["items"]:
        album_id = album["id"]
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

    return {
        "statusCode": 200,
        "body": json.dumps({"alerts_sent": len(alerts)})
    }
