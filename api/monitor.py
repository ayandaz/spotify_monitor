import os
import json
from http.server import BaseHTTPRequestHandler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
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
                    telegram_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
                    requests.post(telegram_url, data={
                        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
                        "text": msg,
                        "parse_mode": "Markdown"
                    })

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
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Method not allowed. Use GET"}).encode("utf-8"))
