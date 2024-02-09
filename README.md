# Feishin RPC

This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

## Installation

> [!IMPORTANT]  
> Feishin RPC is a Linux only application, as it relies on the MPRIS API.

- Install [Python 3.11](https://python.org) or above
- Clone the repository or download the ZIP
- Install dependencies via `python3 -m pip install -r requirements.txt`
- Configure following [Configuration](#configuration)
- Launch via `python3 feishin-rpc.py`

## SystemD

```
[Unit]
Description=Feishin RPC Service
After=network.target

[Service]
Type=simple
ExecStart=python3 /path/to/feishin-rpc.py

[Install]
WantedBy=default.target
```

## Configuration

All configuration goes in `~/.config/iipython/feishin-rpc.toml`.

```toml
# The LOCAL URL of your server (hostnames supported)
# If you want discord to use the art url your client sends, set this AND url_public to ""
# If you aren't planning on using image support, this can be left blank
url = "http://192.168.0.1:8096"

# (optional) Use a public imgproxy server? (needed most of the time)
# Obviously, you can self host your own imgproxy server as desired.
imageproxy_enabled = true
imageproxy_url = "https://images.iipython.dev"

# (optional) The public URL of your server (for port-forwarded album art, passed to imgproxy)
# Leave this BLANK if you don't want to edit the url your client sends
url_public = "https://navidrome.yourdomain.com"

# (optional) Time between MPRIS updates (defaults to 1 second)
# Recommended to be as fast as possible for your hardware without causing
# a major performance impact.
update_time = 0.1

# (optional) The name your client uses to identify itself over the MPRIS dbus API
# You can usually find this using a dbus client such as qdbus, however milage may vary
# Feel free to submit a PR if you get it working with a custom client
client_name = "Feishin"
```