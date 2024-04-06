# Copyright (c) 2024 iiPython

# Modules
import time
import atexit
from pypresence import Presence, PipeClosed, DiscordNotFound

from . import cache, cprint
from .images import image_constructors
from .configuration import config_data

# Handle discord RPC
def connect_discord(rpc: Presence = None) -> Presence:
    if rpc is None:
        rpc = Presence(config_data["app_id"])

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

# Config
time_sens = float(config_data["time_sens"])
create_art_uri = image_constructors[config_data["image_proxy"]]

# Main methods
def perform_update(info: dict, cache_key: tuple) -> None:
    tick_changed = (info["position"] > (cache.position + time_sens)) or \
                        (info["position"] < (cache.position - time_sens))

    # Handle updating
    cache_changed = cache_key != cache.last
    if (cache_changed or tick_changed) and info["name"] is not None:
        track, album, artist, status = info["name"], info["album"], info["artist"], info["status"]
        if (status == "paused") and not info["position"]:
            cache.last = cache_key
            cprint("! Nothing is playing.", "b")
            return clear_rpc()

        # Handle cover art
        art_uri = create_art_uri(info["art"])

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
                small_text = status.capitalize(),
                end = (
                    time.time() + info["length"] - info["position"]
                    if status == "playing" else None
                ),
                type = 0 if config_data["state_type"] == "playing" else 2
            )

        except PipeClosed:
            cprint("✗ Connection to discord lost!", "r")
            connect_discord(rpc)

        cache.last = cache_key

    cache.position = info["position"]
