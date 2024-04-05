# Copyright (c) 2024 iiPython

# Modules
import time
import atexit
from pypresence import Presence, DiscordNotFound, PipeClosed

from .configuration import config_data

# Check for config
if not config_data:
    exit("Missing configuration data, please run feishin-rpc-config first.")

# Colored logging
colors = {"r": 31, "g": 32, "b": 34}
def cprint(message: str, color: str) -> None:
    print(f"\x1b[{colors[color]}m{message}\x1b[0m")

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

# Cache handler
class Cache():
    last, position = None, 0

cache = Cache()
