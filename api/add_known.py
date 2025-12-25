import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.kv_helpers import get_known, set_known

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed. Use POST"})
        }

    try:
        body = json.loads(request.body)
        album_ids = body.get("album_ids", [])

        if not album_ids:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No album_ids provided"})
            }

        # Initialize Spotify client
        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
            )
        )

        current_known = get_known()
        added_albums = []

        for album_id in album_ids:
            try:
                album = sp.album(album_id)
            except spotipy.SpotifyException:
                continue
            current_known.add(album_id)
            added_albums.append(album["name"])

        set_known(current_known)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Added {len(added_albums)} albums to known releases",
                "albums": added_albums
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
