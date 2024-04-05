# Copyright (c) 2024 iiPython

# Modules
import json
from base64 import b64encode

import rel
import websocket

from . import cache, clear_rpc
from .discord import perform_update
from .configuration import config_data

# Start loop
def on_message(ws: websocket.WebSocket, message: bytes) -> None:
    data = json.loads(message.decode())["data"]
    song = data.get("song")
    if song is not None:
        cache.previous_song = song

    song = song or cache.previous_song
    perform_update({
        "art": song["imageUrl"], "name": song["name"], "album": song["album"],
        "artist": song["artistName"], "status": data["status"],
        "length": song["duration"] / 1000, "position": data["currentTime"]
    }, (song["name"], song["album"], song["artistName"], data["status"]))

def on_error(ws: websocket.WebSocket, error: str) -> None:
    clear_rpc()

def on_open(ws: websocket.WebSocket) -> None:
    auth_basic = b64encode(f"{config_data['remote_user']}:{config_data['remote_pass']}".encode()).decode()
    ws.send(json.dumps({"event": "authenticate", "header": f"Basic {auth_basic}"}))

if __name__ == "__main__":
    try:
        ws = websocket.WebSocketApp(
            f"ws://localhost:{config_data['remote_port']}",
            on_open = on_open, on_message = on_message, on_error = on_error
        )
        ws.run_forever(dispatcher = rel, reconnect = 15, skip_utf8_validation = True)
        rel.signal(2, rel.abort)
        rel.dispatch()

    except KeyboardInterrupt:
        pass
