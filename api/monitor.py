import os
import json
from http.server import BaseHTTPRequestHandler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from twilio.rest import Client
from utils.kv_helpers import get_known

ARTIST_ID = os.environ.get("SPOTIFY_ARTIST_ID")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Spotify client
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=os.environ["SPOTIFY_CLIENT_ID"],
                    client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
                )
            )

            # Twilio client
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

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"alerts_sent": len(alerts)}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def do_POST(self):
        # Optional: return 405 for POST
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Method not allowed. Use GET"}).encode("utf-8"))
