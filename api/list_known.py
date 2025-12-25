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

    # Get known album IDs from KV
    known_ids = get_known()

    # Fetch album details from Spotify
    albums = []
    for album_id in known_ids:
        try:
            album = sp.album(album_id)
            albums.append({
                "name": album["name"],
                "release_date": album["release_date"],
                "image": album["images"][0]["url"] if album["images"] else "",
                "spotify_url": album["external_urls"]["spotify"]
            })
        except spotipy.SpotifyException:
            continue  # skip invalid IDs

    # Generate simple HTML
    html = "<html><head><title>Known Albums</title></head><body>"
    html += "<h1>Known Spotify Albums</h1>"
    html += "<div style='display:flex; flex-wrap:wrap;'>"
    for a in albums:
        html += f"""
        <div style='width:200px; margin:10px; text-align:center;'>
            <img src='{a['image']}' width='180' height='180'><br>
            <strong>{a['name']}</strong><br>
            <small>{a['release_date']}</small><br>
            <a href='{a['spotify_url']}' target='_blank'>Listen</a>
        </div>
        """
    html += "</div></body></html>"

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html
    }
