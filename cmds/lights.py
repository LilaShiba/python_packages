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
    "warm": {"r": 255, "g": 170, "b": 0, "effect": None},
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

    # ☕ Cozy & cuddle
    "cuddle": {"r": 255, "g": 0, "b": 200, "effect": "warmth"},
    "cocoa": {"r": 120, "g": 72, "b": 50, "effect": None},
    "lavender": {"r": 200, "g": 170, "b": 255, "effect": "fade"},
    "starlight": {"r": 200, "g": 220, "b": 255, "effect": "sparkle"},
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
