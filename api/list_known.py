import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.kv_helpers import get_known

def handler(request):
    # Spotify client
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
                "id": album_id,  # 👈 REQUIRED for delete
                "name": album["name"],
                "release_date": album["release_date"],
                "image": album["images"][0]["url"] if album["images"] else "",
                "spotify_url": album["external_urls"]["spotify"]
            })
        except spotipy.SpotifyException:
            continue

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(albums)
    }
