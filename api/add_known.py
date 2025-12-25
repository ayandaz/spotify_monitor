import json
import os
from vercel_kv import kv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import parse_qs

KV_KEY = "known_releases"

# Initialize Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
    )
)

def handler(request):
    # Accept GET with query parameter: ?album_id=XYZ
    if request.method != "GET":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed. Use GET with album_id"})
        }

    try:
        query = parse_qs(request.query_string)
        album_id = query.get("album_id", [None])[0]

        if not album_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing album_id parameter"})
            }

        # Validate album with Spotify
        try:
            album = sp.album(album_id)
        except spotipy.SpotifyException:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid album ID: {album_id}"})
            }

        # Add to KV
        current_known = set(kv.get(KV_KEY) or [])
        current_known.add(album_id)
        kv.set(KV_KEY, list(current_known))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Added album '{album['name']}' to known releases",
                "album_id": album_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
