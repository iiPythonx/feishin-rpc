# Copyright (c) 2024 iiPython

# Modules
import os
import sys
import json
from pathlib import Path

import tkinter as tk
from tkinter import ttk

# Configuration file
config_path = (Path(os.getenv("LOCALAPPDATA")) if os.name == "nt" else Path.home() / ".config") / "feishin-rpc"
config_path.mkdir(exist_ok = True)
config_file, config_data = config_path / "config.json", {}
if config_file.is_file():
    config_data = json.loads(config_file.read_text())

# Initialization
class Configuration(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.config(width = 700, height = 200)
        self.title("Feishin RPC Configuration")

        # Constants
        url_proxies = ["imgproxy", "ndip", "imgbb"]

        # Handle config values
        values, widgets = [
            ("app_id", "Application ID", tk.Entry(self, width = 22), "1117545345690374277"),
            ("image_proxy", "Image Proxy", ttk.Combobox(values = ["freeimagehost", *url_proxies], state = "readonly"), "freeimagehost"),
            ("proxy_url", "Proxy URL (ndip/imgproxy)", tk.Entry(self, width = 22), ""),
            ("proxy_key", "API Key (imgbb)", tk.Entry(self, width = 35), ""),
            ("state_type", "State Type", ttk.Combobox(values = ["playing", "listening"], state = "readonly"), "playing"),
            ("arrpc", "arRPC Features (vesktop only)", ttk.Combobox(values = ["on", "off"], state = "readonly"), "on")
        ], {}
        for index, (key, label, widget, default) in enumerate(values):
            if key == "_":
                widget.grid(row = index, columnspan = 2, padx = 5, pady = 5, sticky = tk.W + tk.E)
                continue

            label = tk.Label(self, text = label)
            label.grid(row = index, column = 0, sticky = tk.W, padx = 5, pady = 5)

            # Widget setup
            widgets[key] = widget
            widget.grid(row = index, column = 1, padx = 5, pady = 5)
            if isinstance(widget, ttk.Combobox):
                widget.set(config_data.get(key, default))

            elif isinstance(widget, tk.Entry):
                widget.delete(0, "end")
                widget.insert(0, config_data.get(key, default))

            # Special widget configuration
            match key:
                case "image_proxy":
                    def selection_changed(event) -> None:
                        widgets["proxy_url"].configure(
                            state = "normal" if widgets["image_proxy"].get() in url_proxies else "disabled"
                        )

                    widget.bind("<<ComboboxSelected>>", selection_changed)

                case "proxy_url":
                    widget.configure(state = "normal" if config_data.get("image_proxy") in url_proxies else "disabled")

        # Add save button
        def perform_save():
            for (key, label, widget, default) in values:
                if isinstance(widget, ttk.Combobox):
                    config_data[key] = widget["values"][widget.current()]

                elif isinstance(widget, tk.Entry):
                    config_data[key] = widget.get()

            config_file.write_text(json.dumps(config_data, indent = 4))
            sys.exit()

        set_up_button = tk.Button(self, text = "Save Configuration", command = perform_save)
        set_up_button.grid(row = index + 1, columnspan = 2, padx = 5, pady = 5, sticky = tk.W + tk.E)

# Launch Tk app
def launch():
    Configuration().mainloop()

if __name__ == "__main__":
    launch()
