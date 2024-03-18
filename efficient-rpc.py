# Copyright (c) 2023-2024 iiPython

# Modules
import time
import atexit
import tomllib
from pathlib import Path
from base64 import urlsafe_b64encode

from pydbus import SessionBus
from gi.repository import GLib
from gi.repository.GLib import GError
from pypresence import Presence, PipeClosed, DiscordNotFound

# Load configuration
config_file = Path.home() / ".config/iipython/feishin-rpc.toml"
if not config_file.is_file():
    exit("error: no config file found in .config")

try:
    with config_file.open() as fh:
        config = tomllib.loads(fh.read())
        for k, v in {  # Load default config values
            "update_time": 1, "tick_sensitivity": 2, "imageproxy_enabled": True,
            "imageproxy_url": "https://images.iipython.dev", "url_public": config["url"],
            "client_name": "Feishin", "client_id": "1117545345690374277"
        }.items():
            config[k] = config.get(k) or v

        config["tick_sensitivity"] = float(config["tick_sensitivity"])

except tomllib.TOMLDecodeError:
    exit("error: invaild toml found in config file")

except OSError:
    exit("error: permission error trying to read config file")

# Colored logging
colors = {"r": 31, "g": 32, "b": 34}
def cprint(message: str, color: str) -> None:
    print(f"\x1b[{colors[color]}m{message}\x1b[0m")

# Initialization
loop = GLib.MainLoop()

# Handle discord RPC
def connect_discord(rpc: Presence = None) -> Presence:
    if rpc is None:
        rpc = Presence(config["client_id"])

    while True:
        try:
            rpc.connect()
            cprint("✓ Connected to discord!", "g")
            return rpc

        except DiscordNotFound:
            time.sleep(5)

rpc = connect_discord()

def clear_rpc() -> None:
    try:
        rpc.clear()

    except PipeClosed:
        pass  # Discord died at the same time as us presumably, so maybe this is a system shutdown?

def disconnect_discord() -> None:
    clear_rpc()
    cprint("✓ Disconnected from discord!", "r")

atexit.register(disconnect_discord)

# Cache handler
class Cache():
    last, position = None, 0

cache = Cache()

# Handle updates
bus, feishin_bus = SessionBus(), None
while feishin_bus is None:
    try:
        feishin_bus = bus.get("org.mpris.MediaPlayer2.Feishin", "/org/mpris/MediaPlayer2")

    except GError:
        time.sleep(5)
        pass

def signal_fired(*a) -> None:
    if a[3] == "RunningApplicationsChanged" and a[4][1] and "feishin" in a[4][1][0].lower():
        cprint("✓ Feishin has been closed.", "r")
        return clear_rpc()

    elif a[1] != "/org/mpris/MediaPlayer2":
        return

    try:
        md = feishin_bus.Metadata
        info = {
            "art": md.get("mpris:artUrl"), "name": md.get("xesam:title"), "album": md.get("xesam:album"),
            "artist": md.get("xesam:artist", [None])[0], "status": feishin_bus.PlaybackStatus,

            # Microsecond attributes
            "length": feishin_bus.Metadata.get("mpris:length", 0) / 1000000,
            "position": feishin_bus.Position / 1000000
        }
        cache_key = (info["name"], info["album"], info["artist"], info["status"])
        tick_changed = (info["position"] > (cache.position + config["tick_sensitivity"])) or \
                            (info["position"] < (cache.position - config["tick_sensitivity"]))

    except GError:
        return

    # Handle updating
    cache_changed = cache_key != cache.last
    if (cache_changed or tick_changed) and info["name"] is not None:
        track, album, artist, status = info["name"], info["album"], info["artist"], info["status"]
        if (status == "Paused") and not info["position"]:
            cache.last = cache_key
            cprint("! Nothing is playing.", "b")
            return clear_rpc()

        # Handle cover art
        art_uri = info["art"].replace(config["url"], config["url_public"])
        if "&v=" in art_uri:  # Catch Navidrome since the default links are too large
            art_uri = art_uri.split("&v=")[0] + "&v=1&c=rpc"

        if config["imageproxy_enabled"] and config["imageproxy_url"].strip():
            art_uri = f"{config['imageproxy_url']}/0/{urlsafe_b64encode(art_uri.encode()).rstrip(b'=').decode()}.jpg"

        # Update RPC
        track_status = status if cache_changed else "position update"
        cprint(f"! {track} by {artist} on {album} ({track_status})", "b")
        try:
            rpc.update(
                name = artist,
                state = f"on {album}",
                details = track,
                large_image = art_uri,
                large_text = album,
                small_image = status.lower(),
                small_text = status,
                end = (
                    time.time() + info["length"] - info["position"]
                    if status == "Playing" else None
                )
            )

        except PipeClosed:
            cprint("✗ Connection to discord lost!", "r")
            connect_discord(rpc)

        cache.last = cache_key

    cache.position = info["position"]

signal_fired(0, "/org/mpris/MediaPlayer2", 0, 0)
bus.subscribe(object = "/org/mpris/MediaPlayer2", signal_fired = signal_fired)
bus.subscribe(signal = "RunningApplicationsChanged", signal_fired = signal_fired)

# Start loop
if __name__ == "__main__":
    try:
        loop.run()

    except KeyboardInterrupt:
        pass
