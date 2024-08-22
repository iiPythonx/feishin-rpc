# Copyright (c) 2024 iiPython

# Modules
import json
import atexit
from pathlib import Path

# Handle colored printing
colors = {"r": 31, "g": 32, "b": 34}
def cprint(message: str, color: str) -> None:
    print(f"\x1b[{colors[color]}m{message}\x1b[0m")

# Handle caching
cache_path = Path.home() / ".cache/feishin-rpc/covers.json"
cache_path.parent.mkdir(exist_ok = True, parents = True)

cover_cache = {}
if cache_path.is_file():
    cover_cache = json.loads(cache_path.read_text())

def write_cache() -> None:
    cache_path.write_text(json.dumps(cover_cache))

atexit.register(write_cache)
