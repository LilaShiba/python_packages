import os
import json
import argparse
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────
# 🌙 Load environment variables
# ──────────────────────────────────────────────────────────────
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("GOVEE_API_KEY")
if not API_KEY:
    raise ValueError(f"❌ Missing GOVEE_API_KEY in {dotenv_path}")

# ──────────────────────────────────────────────────────────────
# ⚙️ Constants
# ──────────────────────────────────────────────────────────────
BASE_URL: str = "https://developer-api.govee.com/v1"
CACHE_FILE: Path = Path.home() / ".cache" / "govee_devices.json"

HEADERS: Dict[str, str] = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# ──────────────────────────────────────────────────────────────
# 🌈 Themed RGB color presets with effects
# ──────────────────────────────────────────────────────────────
COLOR_PRESETS: Dict[str, Dict[str, Any]] = {
    # Core tones
    "warm": {"r": 255, "g": 244, "b": 214, "effect": None},
    "cool": {"r": 0, "g": 255, "b": 255, "effect": None},
    "red": {"r": 255, "g": 0, "b": 0, "effect": None},
    "green": {"r": 0, "g": 255, "b": 0, "effect": None},
    "blue": {"r": 0, "g": 0, "b": 255, "effect": None},

    # 🌈 Trans pride inspired
    "trans": {"r": 180, "g": 206, "b": 255, "effect": "pulse"},
    "pride": {"r": 255, "g": 156, "b": 187, "effect": "fade"},

    # 🌙 Witchy
    "witch": {"r": 150, "g": 80, "b": 200, "effect": "breathe"},
    "moon": {"r": 200, "g": 220, "b": 255, "effect": "glimmer"},
    "borg": {"r": 30, "g": 60, "b": 40, "effect": None},
    "kilngon": {"r": 155, "g": 17, "b": 30, "effect": "fade"},


    # ☕ Cozy & cuddle
    "cuddle": {"r": 255, "g": 0, "b": 200, "effect": "warmth"},
    "cocoa": {"r": 120, "g": 72, "b": 50, "effect": None},
    "lavender": {"r": 200, "g": 170, "b": 255, "effect": "fade"},
    "starlight": {"r": 200, "g": 220, "b": 255, "effect": "sparkle"},

    # 🌞 Natural lighting - WARMEST variants
    "sunrise": {"r": 255, "g": 200, "b": 140, "effect": "glow"},
    "morning": {"r": 255, "g": 210, "b": 160, "effect": "glow"},
    "daylight": {"r": 255, "g": 230, "b": 180, "effect": None},
    "golden_hour": {"r": 255, "g": 190, "b": 120, "effect": "warmth"},
    "sunset": {"r": 255, "g": 160, "b": 90, "effect": "fade"},
    "afternoon": {"r": 255, "g": 225, "b": 170, "effect": None},
    "overcast": {"r": 245, "g": 210, "b": 180, "effect": "soft"},


    # 😎 Cool & happy vibes
    "sky_blue": {"r": 135, "g": 206, "b": 235, "effect": "sparkle"},
    "mint": {"r": 152, "g": 255, "b": 152, "effect": "pulse"},
    "sunshine": {"r": 239, "g": 197, "b": 118},  
    "shiba": {"r": 255, "g": 202, "b": 123},
    "lemon": {"r": 255, "g": 250, "b": 150, "effect": "flash"},

    # 🌙 Dreamy & magical shades
    "lavender_dusk": {"r": 200, "g": 180, "b": 255, "effect": "glow"},
    "peach_blossom": {"r": 255, "g": 190, "b": 200, "effect": "soft"},
    "mint_cream": {"r": 245, "g": 255, "b": 240, "effect": "sparkle"},
    "coral_reef": {"r": 255, "g": 127, "b": 80, "effect": "warmth"},
    "twilight_blue": {"r": 100, "g": 149, "b": 237, "effect": "fade"},
    "citrine": {"r": 230, "g": 210, "b": 60, "effect": "flash"},
    "rose_gold": {"r": 255, "g": 182, "b": 193, "effect": "glow"},
    "icy_pearl": {"r": 220, "g": 245, "b": 255, "effect": "pulse"},
    "ember_glow": {"r": 255, "g": 120, "b": 85, "effect": "warmth"},
    "celestial_teal": {"r": 0, "g": 180, "b": 180, "effect": "sparkle"},
    "butterscotch": {"r": 255, "g": 200, "b": 100, "effect": "soft"},
    "frosted_lilac": {"r": 230, "g": 210, "b": 255, "effect": "fade"},

        # 🌈 Expanded Custom Color Palette
    "sunbeam_yellow": {"r": 255, "g": 245, "b": 130, "effect": "flash"},
    "tangerine_twist": {"r": 255, "g": 140, "b": 60, "effect": "warmth"},
    "blush": {"r": 255, "g": 185, "b": 195, "effect": "soft"},
    "orchid_purple": {"r": 218, "g": 112, "b": 214, "effect": "glow"},
    "cerulean": {"r": 42, "g": 82, "b": 190, "effect": "sparkle"},
    "forest_mist": {"r": 85, "g": 140, "b": 110, "effect": "pulse"},
    "copper_coin": {"r": 184, "g": 115, "b": 51, "effect": "warmth"},
    "aqua_marine": {"r": 127, "g": 255, "b": 212, "effect": "fade"},
    "smoky_gray": {"r": 120, "g": 120, "b": 130, "effect": "soft"},
    "midnight": {"r": 25, "g": 25, "b": 112, "effect": "fade"},

        # 🌆 Cyberpunk Palette - One-Word Names
    "fuchsia": {"r": 255, "g": 20, "b": 147, "effect": "glow"},
    "cyan": {"r": 0, "g": 255, "b": 255, "effect": "sparkle"},
    "violet": {"r": 138, "g": 43, "b": 226, "effect": "pulse"},
    "lime": {"r": 150, "g": 255, "b": 50, "effect": "flash"},
    "midnight2": {"r": 48, "g": 25, "b": 52, "effect": "fade"},
    "teal": {"r": 0, "g": 128, "b": 140, "effect": "glow"},
    "magenta": {"r": 255, "g": 0, "b": 255, "effect": "pulse"},
    "chrome": {"r": 200, "g": 200, "b": 210, "effect": "shine"},
    "plasma": {"r": 255, "g": 85, "b": 0, "effect": "glow"},
    "ultraviolet": {"r": 72, "g": 0, "b": 120, "effect": "fade"},
    "neon": {"r": 255, "g": 105, "b": 180, "effect": "sparkle"},
    "electric": {"r": 0, "g": 150, "b": 255, "effect": "flash"},
    "rubyteal": {"r": 155, "g": 60, "b": 100, "effect": "glow"},
    "midnightrose": {"r": 120, "g": 20, "b": 70, "effect": "fade"},   # dark, romantic shadow
    "amethyst": {"r": 180, "g": 90, "b": 220, "effect": "pulse"},     # rich jewel pop
    "plasmaglow": {"r": 255, "g": 80, "b": 50, "effect": "glow"},     # electric warmth
    "emeraldneon": {"r": 0, "g": 180, "b": 130, "effect": "flash"},   # neon-cyber green accent



}

# ──────────────────────────────────────────────────────────────
# 📦 Device management
# ──────────────────────────────────────────────────────────────
def get_devices(refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Retrieve devices from cache or Govee API.
    Cache is saved in ~/.cache/govee_devices.json and reused unless refresh=True.
    """
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Try reading from cache first
    if CACHE_FILE.exists() and not refresh:
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                devices = json.load(f)
                if devices:
                    return devices
        except json.JSONDecodeError:
            print("⚠️ Cache corrupted, refetching from API...")

    print("🔄 Fetching devices from Govee API...")
    response = requests.get(f"{BASE_URL}/devices", headers=HEADERS)
    if response.status_code == 200:
        devices = response.json().get("data", {}).get("devices", [])
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=2)
        return devices

    print(f"⚠️ Error retrieving devices: {response.status_code}")
    print(response.text)
    return []

# ──────────────────────────────────────────────────────────────
# 📋 Pretty-print devices
# ──────────────────────────────────────────────────────────────
def print_device_table(devices: List[Dict[str, Any]]) -> None:
    """Pretty-print a table of available Govee devices."""
    if not devices:
        print("No devices found in cache.")
        return

    print("\n📋 Govee Devices")
    print("=" * 60)
    print(f"{'Name':25} {'Model':15} {'Device ID'}")
    print("-" * 60)
    for d in devices:
        name = d.get("deviceName", "unknown")[:25]
        model = d.get("model", "-")[:15]
        device_id = d.get("device", "-")
        print(f"{name:25} {model:15} {device_id}")
    print("=" * 60)

# ──────────────────────────────────────────────────────────────
# 💡 Device control
# ──────────────────────────────────────────────────────────────
def control_device(device: Dict[str, Any], action: str, effect: Optional[str] = None) -> None:
    """
    Send control command to a specific device.
    - action: 'on', 'off', 'color', or 'brightness'
    - effect: color name or brightness value (int)
    """
    name = device.get("deviceName", "unknown")
    device_id = device.get("device")
    model = device.get("model")

    if not device_id or not model:
        print(f"⚠️ Skipping {name}: missing device ID or model")
        return

    cmd: Dict[str, Any]

    # Handle power state
    if action in ["on", "off"]:
        cmd = {"name": "turn", "value": action}

    # Handle color presets
    elif action == "color" and effect in COLOR_PRESETS:
        preset = COLOR_PRESETS[effect]
        cmd = {"name": "color", "value": {"r": preset["r"], "g": preset["g"], "b": preset["b"]}}

        # Optional: trigger any special "effect" behavior
        if preset.get("effect"):
            print(f"✨ {name}: activating {effect} ({preset['effect']}) mode")

    # Handle brightness
    elif action == "brightness" and isinstance(effect, int):
        cmd = {"name": "brightness", "value": max(0, min(effect, 100))}

    else:
        print(f"⚠️ No valid payload for {name} ({action})")
        return

    payload = {"device": device_id, "model": model, "cmd": cmd}
    response = requests.put(f"{BASE_URL}/devices/control", headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"✅ {name}: {action} {effect if effect else ''}")
    else:
        print(f"⚠️ Error controlling {name} ({action}): {response.status_code}")
        print(response.text)

# ──────────────────────────────────────────────────────────────
# 🧙 CLI entrypoint
# ──────────────────────────────────────────────────────────────
def main() -> None:
    """CLI tool for controlling Govee smart lights with themed presets."""
    parser = argparse.ArgumentParser(description="Control Govee smart lights.")
    parser.add_argument("-s", "--state", choices=["on", "off"], help="Turn device(s) on or off")
    parser.add_argument("-c", "--color", help="Set color (e.g., witch, trans, cuddle)")
    parser.add_argument("-b", "--brightness", type=int, help="Set brightness (0–100)")
    parser.add_argument("-d", "--device", help="Control a specific device by name")
    parser.add_argument("--refresh", action="store_true", help="Refresh device list from Govee API")
    parser.add_argument("--list", action="store_true", help="List all cached devices")
    args = parser.parse_args()

    devices = get_devices(refresh=args.refresh)

    if args.list:
        print_device_table(devices)
        return

    if not devices:
        print("No devices found.")
        return

    # Filter for specific device if requested
    if args.device:
        matches = [d for d in devices if d.get("deviceName") == args.device]
        if not matches:
            print(f"⚠️ Device named '{args.device}' not found.")
            return
        devices = matches

    # Execute actions
    for device in devices:
        name = device.get("deviceName", "unknown")
        print(f"→ Controlling {name}")
        if args.state:
            control_device(device, args.state)
        if args.color:
            control_device(device, "color", args.color)
        if args.brightness is not None:
            control_device(device, "brightness", args.brightness)

# ──────────────────────────────────────────────────────────────
# 🚀 Main entry
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
