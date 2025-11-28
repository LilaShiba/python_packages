# 🐕✨ CLI Tools Suite 🧙‍♀️

A modular command-line toolkit for device control, data retrieval, and network operations — built in **Python 3.13+**.

---

## Overview

This suite provides a unified command interface for interacting with APIs, connected devices, and local systems.  
Each command lives in its own module under `cmds/`, while shared functionality (like networking, environment setup, and I/O) resides in `utils/`.

---

## Command Modules

| Command | Description |
|----------|--------------|
| `wut` | Dictionary and internal command reference utilities. 🐾 |
| `weather` | NOAA weather updates & predictions ✨ |
| `sky` | NASA astronomical object feed and space event info. 🌟 |
| `lights` | Govee smart light controller with preset themes. 🧙‍♀️ |
| `scan` | Local network IP discovery and mapping tool. 🐕 |
| `sensors` | Tricorder-style input manager for connected sensors. 🧙‍♀️ |

---

## Project Structure

<pre><code>.
├── build/
│   └── lib/
│       ├── cmds/
│       └── utils/
├── cmds/
│   ├── define.py
│   ├── lights.py
│   ├── neo.py
│   ├── scan_network.py
│   ├── sky.py
│   ├── weather.py
│   └── ...
├── utils/
│   ├── api_gate.py
│   ├── localize.py
│   └── rpi_light_switch.py
├── setup.py
└── .env
</code></pre>

---

## Key Module: `lights.py`

The `lights` module interfaces with the **Govee REST API** to control smart lights.  
It includes caching, preset color themes, and brightness/state management.

**Features**  
- Device discovery with caching at `~/.cache/govee_devices.json` 🐾  
- Power and brightness control  
- Preset color themes (including custom ones like *trans*, *witch*, *cuddle*) ✨  
- Automatic `.env` key loading and validation 🧙‍♀️

**Environment Variables**

<pre><code>
GOVEE_API_KEY=<your-api-key>
</code></pre>

**Example Usage**

<pre><code>
# List all cached devices
python -m lights --list

# Turn lights on
python -m lights --state on

# Set brightness to 75%
python -m lights --brightness 75

# Activate a color preset
python -m lights --color witch
</code></pre>

---

## Installation

<pre><code>
pip install -e .
</code></pre>

---

## Development Notes

- All modules are import-safe and compatible with standalone CLI execution. 🐕  
- The `.env` file should be placed one directory above the module root for global use. ✨  
- Cached data is stored under the user’s home directory (`~/.cache/`). 🧙‍♀️
