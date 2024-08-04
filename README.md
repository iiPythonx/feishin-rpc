# Feishin RPC


This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

## ARRPC notice

Regular discord RPC has restrictions in place to avoid you changing the application name from a presence update.  

ARRPC does not have this issue, therefore *if* you are using an unmodded client you will **need to disable ARRPC support in the Feishin RPC Configuration**.

Example of the difference between ARRPC support on and off:

| ARRPC (vesktop) | Non-ARRPC (unmodded) |
| --------------- | -------------------- |
| ![Now playing "Eminem"](.github/arrpc.png) | ![Now playing "Feishin"](.github/unmodded.png) |

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
# ExecStart=%h/.feishin-rpc/.venv/bin/feishin-rpc

[Install]
WantedBy=default.target
```

## Configuration

Configuration will go in a centralized location depending on your OS:
- Linux: `~/.config/feishin-rpc/config.json`
- Windows: `%LocalAppData%\feishin-rpc\config.json`

To create the config file for you, run `feishin-rpc-config`.
