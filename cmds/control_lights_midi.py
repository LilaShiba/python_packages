import os
import argparse
import requests
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GOVEE_API_KEY")
BASE_URL = "https://openapi.api.govee.com"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def get_devices():
    """Retrieve all devices and their capabilities."""
    response = requests.get(
        f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error retrieving devices: {response.status_code}")
        return []


def control_device(device, action, color=None, brightness=None):
    """Turn the device on/off or set its color/brightness."""
    if "sku" not in device or "device" not in device or device.get('deviceName') in ['Smart Curtain Lights', 'Sailor moon', 'TV', 'Fan']:
        print(f"Skipping for {device.get('deviceName', 'unknown')}")
        return

    # Power On/Off Action
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
        response = requests.post(
            f"{BASE_URL}/router/api/v1/device/control", headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Successfully turned {action} {device.get('deviceName', 'unknown')}")
        else:
            print(f"Error turning {action} {device.get('deviceName', 'unknown')}: {response.status_code}")

    # Set Color Action
    if action == "color" and color:
        payload = {
            "requestId": "unique-request-id",
            "payload": {
                "sku": device["sku"],
                "device": device["device"],
                "capability": {
                    "type": "devices.capabilities.color",
                    "instance": "color",
                    "value": color
                }
            }
        }
        response = requests.post(
            f"{BASE_URL}/router/api/v1/device/control", headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Successfully set color to {color} for {device.get('deviceName', 'unknown')}")
        else:
            print(f"Error setting color for {device.get('deviceName', 'unknown')}: {response.status_code}")

    # Set Brightness Action
    if action == "brightness" and brightness:
        payload = {
            "requestId": "unique-request-id",
            "payload": {
                "sku": device["sku"],
                "device": device["device"],
                "capability": {
                    "type": "devices.capabilities.brightness",
                    "instance": "brightness",
                    "value": brightness
                }
            }
        }
        response = requests.post(
            f"{BASE_URL}/router/api/v1/device/control", headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Successfully set brightness to {brightness} for {device.get('deviceName', 'unknown')}")
        else:
            print(f"Error setting brightness for {device.get('deviceName', 'unknown')}: {response.status_code}")


def get_preset_color(color_name):
    """Return a preset color."""
    color_presets = {
        "warm": "#FFAA00",  # Warm Yellow
        "cool": "#00FFFF",  # Cool Blue
        "red": "#FF0000",   # Red
        "green": "#00FF00", # Green
        "blue": "#0000FF"   # Blue
    }
    return color_presets.get(color_name.lower(), "#FFFFFF")  # Default to white if color is unknown


def main():
    parser = argparse.ArgumentParser(
        description="Control Govee devices on/off, set color or brightness.")
    parser.add_argument("-s", "--state", choices=["on", "off", "color", "brightness"], required=True,
                        help="Turn devices on/off or set color/brightness")
    parser.add_argument("-c", "--color", type=str, help="Set the color (e.g., warm, cool, red, green, blue)")
    parser.add_argument("-b", "--brightness", type=int, choices=range(1, 101), help="Set brightness (1-100)")
    args = parser.parse_args()

    if args.state == "color" and not args.color:
        print("Please specify a color using -c option.")
        return

    devices = get_devices()
    for device in devices:
        if args.state == "on" or args.state == "off":
            control_device(device, args.state)
        elif args.state == "color":
            color = get_preset_color(args.color)
            control_device(device, args.state, color=color)
        elif args.state == "brightness" and args.brightness:
            control_device(device, args.state, brightness=args.brightness)


if __name__ == "__main__":
    main()
