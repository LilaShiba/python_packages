import os
import argparse
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOVEE_API_KEY")
BASE_URL = "https://openapi.api.govee.com"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Preset colors
color_presets = {
    "warm": "#FFAA00",   # Warm Yellow
    "cool": "#00FFFF",   # Cool Blue
    "red": "#FF0000",    # Red
    "green": "#00FF00",  # Green
    "blue": "#0000FF"    # Blue
}

def get_devices():
    """Retrieve all devices and their capabilities."""
    response = requests.get(f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error retrieving devices: {response.status_code}")
        return []

def control_device(device, action, effect=None):
    """Send control command to the device."""
    if "sku" not in device or "device" not in device or device.get('deviceName') in ['Smart Curtain Lights', 'Sailor moon', 'TV', 'Fan']:
        print(f"Skipping for {device.get('deviceName', 'unknown')}")
        return

    payload = None

    if action in ["on", "off"]:
        value = 1 if action == "on" else 0
        payload = {
            "requestId": "unique-request-id",
            "payload": {
                "sku": device["sku"],
                "device": device["device"],
                "capability": {
                    "type": "devices.capabilities.on_off",
                    "instance": "powerSwitch",
                    "value": value
                }
            }
        }

    elif action == "color" and effect in color_presets:
        payload = {
            "requestId": "unique-request-id",
            "payload": {
                "sku": device["sku"],
                "device": device["device"],
                "capability": {
                    "type": "devices.capabilities.color",
                    "instance": "color",
                    "value": color_presets[effect]
                }
            }
        }

    elif action == "brightness" and isinstance(effect, int):
        payload = {
            "requestId": "unique-request-id",
            "payload": {
                "sku": device["sku"],
                "device": device["device"],
                "capability": {
                    "type": "devices.capabilities.brightness",
                    "instance": "brightness",
                    "value": effect
                }
            }
        }

    if payload:
        response = requests.post(f"{BASE_URL}/router/api/v1/device/control", headers=HEADERS, json=payload)
        if response.status_code == 200:
            if action == "color":
                print(f"Successfully set color to {effect}")
            else:
                print(f"Successfully set {action} for {device.get('deviceName', 'unknown')}")
        else:
            print(f"Error setting {action} for {device.get('deviceName', 'unknown')}: {response.status_code}")
    else:
        print(f"No valid payload for action: {action}")

def main():
    parser = argparse.ArgumentParser(description="Control Govee devices on or off.")
    parser.add_argument("-s", "--state", choices=["on", "off"], help="Turn devices on or off")
    parser.add_argument("-c", "--color", help="Set device color (e.g., red, blue, warm)")
    parser.add_argument("-d", "--device", help="Control only one device by name")
    args = parser.parse_args()

    devices = get_devices()
    device_lookup = {d.get("deviceName"): d for d in devices}

    if args.device:
        if args.device in device_lookup:
            devices = [device_lookup[args.device]]  # Wrap in list so the loop works
        else:
            print(f"Device named '{args.device}' not found.")
            return

    for device in devices:
        print(f"Controlling: {device.get('deviceName')}")
        if args.state:
            control_device(device, args.state)
        if args.color:
            control_device(device, "color", args.color)

if __name__ == "__main__":
    main()
