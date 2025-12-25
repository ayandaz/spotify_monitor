import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from twilio.rest import Client
from dotenv import load_dotenv

# Load secrets
load_dotenv()

# ===== CONFIG =====
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox
ARTIST_ID = "69eRfY40RjSFzOToECdiS"
STATE_FILE = "known_releases.json"
# ==================

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def load_known():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_known(data):
    with open(STATE_FILE, "w") as f:
        json.dump(list(data), f)

known = load_known()

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
            f"🚨 *NEW SPOTIFY RELEASE*\n"
            f"🎵 {album['name']}\n"
            f"📅 {album['release_date']}\n"
            f"🔗 {album['external_urls']['spotify']}"
        )

if alerts:
    for msg in alerts:
        twilio.messages.create(
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP,
            body=msg
        )

save_known(current)
