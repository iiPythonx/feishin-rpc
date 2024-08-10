# Feishin RPC

This is a Python app that displays the currently playing song from [Feishin](https://github.com/jeffvli/feishin) on your discord profile.  
It's designed to use minimal resources, while still being as fast (and accurate) as possible.  

This app supports both Navidrome and Jellyfin (and should work with any Feishin-compatible version).

## Notices

Feishin RPC depends on the fact that some modded clients use [arRPC](https://github.com/OpenAsar/arrpc) instead of the normal discord RPC.

<details>
<summary>Not using a client like Vesktop?</summary>
<br>
If you aren't using a client like <a href = "https://github.com/Vencord/Vesktop">Vesktop</a>, you need to disable <i>arRPC Features</i> in the Feishin RPC Configuration.
<br>
Example of the difference between arRPC support on and off:
<br> <br>

| arRPC (vesktop) | Non-arRPC (unmodded) |
| --------------- | -------------------- |
| ![Now playing "Eminem"](.github/arrpc.png) | ![Now playing "Feishin"](.github/unmodded.png) |

</details>
<br>

**Additionally**, you should use mpv over web player for the most painless experience due to some lasting bugs in Feishin's MPRIS implementation.

## Installation

Ensure you have [Python 3.11+](https://python.org/downloads) and [git](https://git-scm.com/) before proceeding.

<details open>
<summary><b>Recommended installation</b></summary>

```sh
# Create a folder for the RPC
mkdir ~/.feishin-rpc && cd ~/.feishin-rpc

# Handle venv creation for package isolation
uv venv --system-site-packages
source .venv/bin/activate

# Install latest version from git
uv pip install git+https://github.com/iiPythonx/feishin-rpc
```

</details>

<details>
<summary><b>Last resort installation option</b></summary>

```sh
pip install --break-system-packages git+https://github.com/iiPythonx/feishin-rpc
```

</details>

---

If you're on a distribution like Arch Linux, you might also need to:
```sh
sudo pacman -S python-gobject
```

## Usage

Configuration will go in a centralized location depending on your OS:
- Linux: `~/.config/feishin-rpc/config.json`
- Windows: `%LocalAppData%\feishin-rpc\config.json`

To create the config file for you, run `feishin-rpc-config`.  
**Afterwards, you can launch the RPC by running `feishin-rpc`.**

## Systemd

```conf
[Unit]
Description=Feishin RPC Service
After=network.target

[Service]
Type=simple

# If you installed Feishin RPC locally:
ExecStart=%h/.feishin-rpc/.venv/bin/feishin-rpc

# Otherwise, uncomment the following:
# ExecStart=python3 -m feishin-rpc

[Install]
WantedBy=default.target
```
