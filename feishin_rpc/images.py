# Copyright (c) 2024 iiPython

# Modules
import requests
from base64 import urlsafe_b64encode

from .config import config_data

# Initialization
proxy_url = config_data["proxy_url"]
imgbb_key = config_data["imgbb_key"]

# Constructors
session = requests.Session()
def construct_freeimagehost(art_url: str) -> str:
    with session.get(art_url, verify = False) as source:
        resp = session.post(
            "https://freeimage.host/api/1/upload",
            files = {"source": source.content},
            params = {"key": "6d207e02198a847aa98d0a2a901485a5", "action": "upload"}
        ).json()
        return resp["image"]["url"]
    
def construct_imgbb(art_url: str) -> str:
    with session.get(art_url, verify = False) as source:
        resp = session.post(
            "https://api.imgbb.com/1/upload",
            files = {"image": source.content},
            params = {"key": imgbb_key}
        ).json()
        return resp["data"]["url"]

def construct_imgproxy(art_url: str) -> str:
    if "&v=" in art_url:  # Catch Navidrome since the default links are too large
        art_url = art_url.split("&v=")[0] + "&v=1&c=rpc"

    return f"{proxy_url.rstrip('/')}/0/{urlsafe_b64encode(art_url.encode()).rstrip(b'=').decode()}.jpg"

image_constructors = {
    "freeimagehost": construct_freeimagehost,
    "imgproxy": construct_imgproxy,
    "imgbb": construct_imgbb,
    "ndip": lambda x: f"{proxy_url.rstrip('/')}/image/{x.split('?id=')[1].split('&')[0]}" 
}
