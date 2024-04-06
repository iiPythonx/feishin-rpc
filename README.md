# Feishin RPC


This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

> [!WARNING]  
> Feishin-RPC will **only** work with [Vesktop](https://github.com/Vencord/Vesktop) (or any other client that uses [arrpc](https://github.com/OpenAsar/arrpc)). This is due to discord RPC limitations, and currently can't be bypassed.

## Installation

- Install [Python 3.11+](https://python.org) as well as [git](https://git-scm.com).
- Run `pip install git+https://github.com/iiPythonx/feishin-rpc`.
- Make a config file following [Configuration](#configuration).
- Launch by running `feishin-rpc`.

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

Configuration will go in a centralized location depending on your OS:
- Linux: `~/.config/feishin-rpc/config.json`
- Windows: `%LocalAppData%\feishin-rpc\config.json`

To create the config file for you, run `feishin-rpc-config`.
