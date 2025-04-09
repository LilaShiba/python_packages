import os
import argparse
import requests
from dotenv import load_dotenv

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


def control_device(device, action):
    """Turn the device on or off."""
    if "sku" not in device or "device" not in device or device.get('deviceName') in ['Smart Curtain Lights', 'Sailor moon', 'TV', 'Fan']:
        print(
            f"Skipping for {device.get('deviceName', 'unknown')}")
        return

    value = 1 if action == "on" else 0
    payload = {
        "requestId": "unique-request-id",  # Generate a unique ID for each request
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
        print(
            f"Successfully turned {action} {device.get('deviceName', 'unknown')}")
    else:
        print(
            f"Error turning {action} {device.get('deviceName', 'unknown')}: {response.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Control Govee devices on or off.")
    parser.add_argument("-s", "--state", choices=["on", "off"], required=True,
                        help="Turn devices on or off")
    args = parser.parse_args()

    devices = get_devices()
    for device in devices:
        control_device(device, args.state)


if __name__ == "__main__":
    main()
