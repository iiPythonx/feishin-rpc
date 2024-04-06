# Copyright (c) 2024 iiPython

# Colored logging
colors = {"r": 31, "g": 32, "b": 34}
def cprint(message: str, color: str) -> None:
    print(f"\x1b[{colors[color]}m{message}\x1b[0m")

# Cache handler
class Cache():
    last, position = None, 0
    previous_song = None

cache = Cache()
