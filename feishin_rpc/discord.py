# Copyright (c) 2024 iiPython

# Modules
import time
from pypresence import PipeClosed

from . import rpc, cache, cprint, clear_rpc, connect_discord
from .images import image_constructors
from .configuration import config_data

# Config
tick_sens = float(config_data["tick_sens"])
create_art_uri = image_constructors[config_data["image_proxy"]]

# Main methods
def perform_update(info: dict, cache_key: tuple) -> None:
    tick_changed = (info["position"] > (cache.position + tick_sens)) or \
                        (info["position"] < (cache.position - tick_sens))

    # Handle updating
    cache_changed = cache_key != cache.last
    if (cache_changed or tick_changed) and info["name"] is not None:
        track, album, artist, status = info["name"], info["album"], info["artist"], info["status"]
        if (status == "Paused") and not info["position"]:
            cache.last = cache_key
            cprint("! Nothing is playing.", "b")
            return clear_rpc()

        # Handle cover art
        art_uri = create_art_uri(info["art"], config_data["proxy_url"])

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
