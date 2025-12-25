import json
from http.server import BaseHTTPRequestHandler
from utils.kv_helpers import get_known, set_known

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body_raw = self.rfile.read(content_length)
            body = json.loads(body_raw)

            album_ids = body.get("album_ids", [])
            if not album_ids:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No album_ids provided"}).encode("utf-8"))
                return

            current_known = get_known()
            removed = []

            for album_id in album_ids:
                if album_id in current_known:
                    current_known.remove(album_id)
                    removed.append(album_id)

            set_known(current_known)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": f"Removed {len(removed)} albums from known releases",
                "removed_album_ids": removed
            }).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def do_GET(self):
        # Optional: return 405 for GET on this endpoint
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Method not allowed. Use POST"}).encode("utf-8"))
