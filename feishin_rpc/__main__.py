# Copyright (c) 2024 iiPython

# Modules
import time
import atexit
from pydbus import SessionBus
from gi.repository.GLib import MainLoop, GError  # type: ignore
from pypresence import Presence, PipeClosed, DiscordNotFound

from . import cprint
from .config import config_data
from .images import image_constructors

# Initialization
construct_url = image_constructors[config_data["image_proxy"]]

class Applications:
    DISCORD = "vesktop.desktop"
    FEISHIN = "feishin.desktop"

class FeishinRPC():
    def __init__(self) -> None:
        self.bus = SessionBus()
        self.bus.subscribe(sender = "org.mpris.MediaPlayer2.Feishin", object = "/org/mpris/MediaPlayer2", signal_fired = self._media_change_fire)
        self.bus.subscribe(signal = "RunningApplicationsChanged", signal_fired = self._application_change_fire)

        self.loop = MainLoop()

        # State data
        self._feishin, self._discord = None, None

    def _media_change_fire(self, *args) -> None:
        if not (self._discord and self._feishin):
            return

        try:
            metadata = self._feishin.Metadata
            info = {
                "art": metadata.get("mpris:artUrl"), "name": metadata.get("xesam:title"), "album": metadata.get("xesam:album"),
                "artist": metadata.get("xesam:artist", [None])[0], "status": self._feishin.PlaybackStatus,

                # Microsecond attributes
                "length": self._feishin.Metadata.get("mpris:length", 0) / 1000000,
                "position": self._feishin.Position / 1000000
            }

        except GError:
            return self.disconnect_feishin()

        # Fetch data
        track, album, artist, status = info["name"], info["album"], info["artist"], info["status"]
        if (status == "Paused") and not info["position"]:
            cprint("! Nothing is playing.", "b")
            return self._discord.clear()

        # Grab image URL
        try:
            image_url = construct_url(info["art"], config_data["image_proxy"] == "imgbb" and config_data["proxy_key"] or None)

        except Exception:
            image_url = "placeholder"
            cprint(f"✗ Failed to proxy cover art for {album}.", "r")

        # Update RPC
        cprint(f"! {track} by {artist} on {album} ({'seeked' if args and args[3] == 'Seeked' else status.lower()})", "b")
        try:
            self._discord.update(
                state = f"on {album}",
                details = track,
                large_image = image_url,
                large_text = album,
                small_image = status.lower(),
                small_text = status,

                # Calculate end time
                **(
                    {"end": time.time() + info["length"] - info["position"]}
                    if status == "Playing" else {}
                ),

                # Handle sending name payload (arrpc clients only)
                **(
                    {"name": artist}
                    if config_data["arrpc"] == "on" else {}
                )
            )

        except PipeClosed:
            cprint("✗ Connection to discord lost!", "r")
            self._discord = None

    # Connection handlers
    def disconnect_discord(self) -> None:
        if self._discord is None:
            return
        
        self._discord.clear()
        cprint("✓ Disconnected from discord!", "r")

    def connect_discord(self) -> None:
        try:
            self._discord = Presence(config_data["app_id"])
            self._discord.connect()
            atexit.register(self.disconnect_discord)
            cprint("✓ Connected to discord!", "g")

        except DiscordNotFound:
            pass

    def disconnect_feishin(self) -> None:
        if self._discord is not None:
            self._discord.clear()

        self._feishin = None
        cprint("✓ Disconnected from Feishin!", "r")

    def connect_feishin(self) -> None:
        try:
            self._feishin = self.bus.get("org.mpris.MediaPlayer2.Feishin", "/org/mpris/MediaPlayer2")
            cprint("✓ Connected to Feishin!", "g")

            # Fire in case we already have audio playing
            self._media_change_fire()

        except GError:
            pass

    # Handle application changes
    def _application_change_fire(self, v: str, o: str, i: str, s: str, changes: tuple) -> None:
        if not changes:
            return

        opened, closed = [[app.split("/")[-1] for app in section] for section in changes]
        if Applications.DISCORD in closed:
            self._discord = None
            atexit.unregister(self.disconnect_discord)
            cprint("✓ Disconnected from discord!", "r")

        if Applications.FEISHIN in closed:
            self.disconnect_feishin()

        if Applications.DISCORD in opened:
            self.connect_discord()

        if Applications.FEISHIN in opened:
            self.connect_feishin()

    def start(self) -> None:

        # Attempt initial connections
        self.connect_discord()
        self.connect_feishin()

        # Run GLib loop for dbus listening
        try:
            self.loop.run()

        except KeyboardInterrupt:
            pass

def main() -> None:
    FeishinRPC().start()

if __name__ == "__main__":
    main()
