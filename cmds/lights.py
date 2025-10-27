import os
import json
import argparse
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env from one directory up
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("GOVEE_API_KEY")
if not API_KEY:
    raise ValueError(f"❌ Missing GOVEE_API_KEY in {dotenv_path}")

BASE_URL = "https://developer-api.govee.com/v1"
CACHE_FILE = Path.home() / ".cache" / "govee_devices.json"

HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Preset RGB colors
COLOR_PRESETS = {
    "warm": {"r": 255, "g": 170, "b": 0},
    "cool": {"r": 0, "g": 255, "b": 255},
    "red": {"r": 255, "g": 0, "b": 0},
    "green": {"r": 0, "g": 255, "b": 0},
    "blue": {"r": 0, "g": 0, "b": 255}
}


def get_devices(refresh=False):
    """Retrieve devices from cache or API."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load from cache if it exists and not refreshing
    if CACHE_FILE.exists() and not refresh:
        try:
            with open(CACHE_FILE, "r") as f:
                devices = json.load(f)
                if devices:
                    return devices
        except json.JSONDecodeError:
            pass  # Fall through to refresh

    print("🔄 Fetching devices from Govee API...")
    response = requests.get(f"{BASE_URL}/devices", headers=HEADERS)
    if response.status_code == 200:
        devices = response.json().get("data", {}).get("devices", [])
        with open(CACHE_FILE, "w") as f:
            json.dump(devices, f, indent=2)
        return devices

    print(f"⚠️ Error retrieving devices: {response.status_code}")
    print(response.text)
    return []


def control_device(device, action, effect=None):
    """Send control command to the device."""
    name = device.get("deviceName", "unknown")
    device_id = device.get("device")
    model = device.get("model")

    if not device_id or not model:
        print(f"⚠️ Skipping {name}: missing device ID or model")
        return

    if action in ["on", "off"]:
        cmd = {"name": "turn", "value": action}
    elif action == "color" and effect in COLOR_PRESETS:
        cmd = {"name": "color", "value": COLOR_PRESETS[effect]}
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


def main():
    parser = argparse.ArgumentParser(description="Control Govee smart lights.")
    parser.add_argument("-s", "--state", choices=["on", "off"], help="Turn device(s) on or off")
    parser.add_argument("-c", "--color", help="Set color (e.g., red, blue, warm)")
    parser.add_argument("-b", "--brightness", type=int, help="Set brightness (0–100)")
    parser.add_argument("-d", "--device", help="Control a specific device by name")
    parser.add_argument("--refresh", action="store_true", help="Refresh device list from Govee API")
    args = parser.parse_args()

    devices = get_devices(refresh=args.refresh)
    if not devices:
        print("No devices found.")
        return

    if args.device:
        matches = [d for d in devices if d.get("deviceName") == args.device]
        if not matches:
            print(f"⚠️ Device named '{args.device}' not found.")
            return
        devices = matches

    for device in devices:
        name = device.get("deviceName", "unknown")
        print(f"→ Controlling {name}")
        if args.state:
            control_device(device, args.state)
        if args.color:
            control_device(device, "color", args.color)
        if args.brightness is not None:
            control_device(device, "brightness", args.brightness)


if __name__ == "__main__":
    main()
