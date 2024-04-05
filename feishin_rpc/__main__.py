# Copyright (c) 2024 iiPython

# Modules
import os
import time

if os.name == "nt":
    pass

else:
    from pydbus import SessionBus
    from gi.repository import GLib
    from gi.repository.GLib import GError

from . import cprint, clear_rpc
from .discord import perform_update

# Main loop
def main_loop_windows() -> None:
    pass

def main_loop_linux() -> None:
    loop = GLib.MainLoop()

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
            perform_update(info, (info["name"], info["album"], info["artist"], info["status"]))

        except GError:
            return

    # Hook signals
    signal_fired(0, "/org/mpris/MediaPlayer2", 0, 0)
    bus.subscribe(object = "/org/mpris/MediaPlayer2", signal_fired = signal_fired)
    bus.subscribe(signal = "RunningApplicationsChanged", signal_fired = signal_fired)

    # Launch loop
    loop.run()

# Start loop
if __name__ == "__main__":
    try:
        (main_loop_windows if os.name == "nt" else main_loop_linux)()

    except KeyboardInterrupt:
        pass
