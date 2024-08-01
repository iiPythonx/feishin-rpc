# Feishin RPC


This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

> [!WARNING]  
> Feishin-RPC will **only** work with [Vesktop](https://github.com/Vencord/Vesktop) (or any other client that uses [arrpc](https://github.com/OpenAsar/arrpc)). This is due to discord RPC limitations, and currently can't be bypassed.

## Installation

**Prerequisites:**
- Install [Python 3.11+](https://python.org) as well as [git](https://git-scm.com).

**The recommended way of installing:**

```sh
# Create a folder for the RPC
mkdir ~/.feishin-rpc && cd ~/.feishin-rpc

# Handle venv creation for package isolation
uv venv
source .venv/bin/activate

# Install latest version from git
uv pip install git+https://github.com/iiPythonx/feishin-rpc
```

**The last resort option:**
- Run `pip install --break-system-packages git+https://github.com/iiPythonx/feishin-rpc`.

**After installation:**
- Make a config file following [Configuration](#configuration).
- Launch by running `feishin-rpc`.

## Systemd

```conf
[Unit]
Description=Feishin RPC Service
After=network.target

[Service]
Type=simple

# If you installed Feishin RPC globally:
ExecStart=python3 -m feishin-rpc

# Otherwise, uncomment the following:
# ExecStart=%h/.feishin-rpc/.venv/bin/python3 -m feishin_rpc

[Install]
WantedBy=default.target
```

## Configuration

Configuration will go in a centralized location depending on your OS:
- Linux: `~/.config/feishin-rpc/config.json`
- Windows: `%LocalAppData%\feishin-rpc\config.json`

To create the config file for you, run `feishin-rpc-config`.
