# Feishin RPC

This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

## Installation

> [!IMPORTANT]  
> You will need git installed if you plan to install via pip.

- Install [Python 3.11](https://python.org) or above
- Run `pip install git+https://github.com/iiPythonx/feishin-rpc`
- Configure following [Configuration](#configuration)
- Launch by running `feishin-rpc`

## Systemd

```
[Unit]
Description=Feishin RPC Service
After=network.target

[Service]
Type=simple
ExecStart=python3 -m feishin-rpc

[Install]
WantedBy=default.target
```

## Configuration

Configuration will go in either:
- Linux: `~/.config/feishin-rpc/config.json`
- Windows: `%LocalAppData%\feishin-rpc\config.json`

To create the config file for you, run `feishin-rpc-config`.
