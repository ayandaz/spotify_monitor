import json
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

        current_known = get_known()
        removed = []

        for album_id in album_ids:
            if album_id in current_known:
                current_known.remove(album_id)
                removed.append(album_id)

        set_known(current_known)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Removed {len(removed)} albums from known releases",
                "removed_album_ids": removed
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
