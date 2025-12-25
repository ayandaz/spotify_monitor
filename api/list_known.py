import os
import json
from http.server import BaseHTTPRequestHandler
from utils.kv_helpers import get_known
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
            )
        )
        known_ids = get_known()
        albums = []
        for album_id in known_ids:
            try:
                album = sp.album(album_id)
                albums.append({
                    "id": album_id,
                    "name": album["name"],
                    "release_date": album["release_date"],
                    "image": album["images"][0]["url"] if album["images"] else "",
                    "spotify_url": album["external_urls"]["spotify"]
                })
            except:
                pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(albums).encode("utf-8"))
        return
