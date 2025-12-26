import os
import json
from http.server import BaseHTTPRequestHandler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.kv_helpers import get_known

ARTIST_ID = os.environ.get("SPOTIFY_ARTIST_ID")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
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

            suspicious = []

            for album in results["items"]:
                if album["id"] not in known:
                    suspicious.append({
                        "id": album["id"],
                        "name": album["name"],
                        "release_date": album["release_date"],
                        "image": album["images"][0]["url"] if album["images"] else "",
                        "spotify_url": album["external_urls"]["spotify"]
                    })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(suspicious).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": str(e)}).encode("utf-8")
            )

    def do_POST(self):
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"error": "Method not allowed. Use GET"}).encode("utf-8")
        )
