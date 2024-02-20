#!/usr/bin/env python3
# Copyright (c) 2023-2024 iiPython

# This file is SPECIFICALLY DESIGNED for use with Feishin (github.com/jeffvli/feishin)
# However, it MAY OR MAY NOT work with other clients. Feel free to test it out.

# Modules
import atexit
import tomllib
from pathlib import Path
from getpass import getuser
from time import time, sleep
from base64 import urlsafe_b64encode

from pydbus import SessionBus
from gi.repository.GLib import GError
from pypresence import Presence, PipeClosed, DiscordNotFound

# Initialization
mp2 = "org.mpris.MediaPlayer2"

# Load configuration
config = None
for location in [
    f"/home/{getuser()}/.config/iipython/feishin-rpc.toml",
    "/etc/feishin-rpc.toml"
]:
    location = Path(location)
    if location.is_file():
        try:
            with open(location, "r") as fh:
                config = tomllib.loads(fh.read())

        except tomllib.TOMLDecodeError:
            exit(f"error: invalid toml found in {location}")

        except PermissionError:
            pass  # What else would error? Pretty sure just perms

if config is None:
    exit("error: no valid configuration file found")

UPDATE_TIME = float(config.get("update_time", 1))
TICK_SENS = UPDATE_TIME + float(config.get("tick_sensitivity", 2))
USE_IMGPROXY = config.get("imageproxy_enabled") is True
IMGPROXY_URL = config.get("imageproxy_url", "https://images.iipython.dev")
PUB_ENDPOINT = config.get("url_public", config["url"])
CLIENT_NAME = config.get("client_name", "Feishin")

# Colored logging
colors = {"r": 31, "g": 32, "b": 34}
def cprint(message: str, color: str) -> None:
    print(f"\x1b[{colors[color]}m{message}\x1b[0m")

# Handle RPC
while True:
    try:
        rpc = Presence(config.get("client_id", "1117545345690374277"))
        rpc.connect()
        break

    except DiscordNotFound:
        sleep(UPDATE_TIME)

cprint("✓ Connected to discord!", "g")

# Ensure RPC is cleared at exit
def clear_rpc() -> None:
    try:
        rpc.clear()

    except PipeClosed:

        # Discord died at the same time as us presumably, so maybe this is a system shutdown?
        pass

def onexit() -> None:
    clear_rpc()
    cprint("✓ Disconnected from discord!", "r")

atexit.register(clear_rpc)

# Handle Feishin
class FeishinMPRISReader(object):
    def __init__(self) -> None:
        self.bus, self.connected = SessionBus(), False
        self.connect()

    def connect(self) -> None:
        self.last, self.position = None, 0
        while True:
            try:
                self.feishin = self.bus.get(f"{mp2}.{CLIENT_NAME}", "/org/mpris/MediaPlayer2")
                cprint("✓ Connected to MPRIS!", "g")
                break

            except GError:
                sleep(1)

    def get_current(self) -> dict | None:
        try:
            md = self.feishin.Metadata
            self.connected = True
            return {
                "art": md.get("mpris:artUrl"),
                "name": md.get("xesam:title"),
                "album": md.get("xesam:album"),
                "artist": md.get("xesam:artist", [None])[0],
                "status": self.feishin.PlaybackStatus,

                # Microsecond attributes
                "length": md.get("mpris:length", 0) / 1000000,
                "position": self.feishin.Position / 1000000
            }

        except GError:
            if not self.connected:
                return

            self.connected = False
            cprint("! Feishin has been closed.", "b")
            clear_rpc()
            self.connect()

feishin = FeishinMPRISReader()

# Updating
def update() -> None:

    # Fetch current track info
    info = feishin.get_current()
    if info is None:
        return

    cache_key = (info["name"], info["album"], info["artist"], info["status"])
    tick_changed = (info["position"] > (feishin.position + TICK_SENS)) or \
                        (info["position"] < (feishin.position - TICK_SENS))

    # Handle updating
    cache_changed = cache_key != feishin.last
    if (cache_changed or tick_changed) and info["name"] is not None:
        track, album, artist, status = info["name"], info["album"], info["artist"], info["status"]
        if (status == "Paused") and not info["position"]:
            feishin.last = cache_key
            return clear_rpc()

        # Handle cover art
        art_uri = info["art"].replace(config["url"], PUB_ENDPOINT)
        if "&v=" in art_uri:  # Catch Navidrome since the default links are too large
            art_uri = art_uri.split("&v=")[0] + "&v=1&c=rpc"

        if USE_IMGPROXY and IMGPROXY_URL.strip():
            art_uri = f"{IMGPROXY_URL}/0/{urlsafe_b64encode(art_uri.encode()).rstrip(b'=').decode()}.jpg"

        # Update RPC
        track_status = status if cache_changed else "position update"
        cprint(f"! {track} by {artist} on {album} ({track_status})", "b")
        rpc.update(
            name = artist,
            state = f"on {album}",
            details = track,
            large_image = art_uri,
            large_text = album,
            small_image = status.lower(),
            small_text = status,
            end = (
                time() + info["length"] - info["position"]
                if status == "Playing" else None
            )
        )
        feishin.last = cache_key

    feishin.position = info["position"]

# Mainloop
if __name__ == "__main__":
    while True:
        try:
            update()

        except KeyboardInterrupt:
            break

        except PipeClosed:
            try:
                rpc.connect()

            except DiscordNotFound:
                pass  # This is fine, so dw

        sleep(UPDATE_TIME)

    onexit()
