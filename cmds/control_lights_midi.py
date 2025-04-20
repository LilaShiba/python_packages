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

class Light:
    def __init__(self, device):
        self.device_name = device.get('deviceName')
        self.sku = device.get('sku')
        self.device_id = device.get('device')
        self.power_state = device.get('powerState', 'off')  # Assuming the state is in the device data

    def ensure_light_on(self):
        """Ensure that the light is on before proceeding with any other actions."""
        if self.power_state != "on":
            print(f"Light {self.device_name} is off. Turning it on first...")
            self.control("on")

    def control(self, action, color=None, brightness=None):
        """Turn the device on/off or set its color/brightness."""
        if action in ["on", "off"]:
            value = 0 if action == "off" else 1
            payload = {
                "requestId": "unique-request-id",
                "payload": {
                    "sku": self.sku,
                    "device": self.device_id,
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
                print(f"Successfully turned {action} {self.device_name}")
                self.power_state = action  # Update power state
            else:
                print(f"Error turning {action} {self.device_name}: {response.status_code}")

        if action == "color" and color:
            payload = {
                "requestId": "unique-request-id",
                "payload": {
                    "sku": self.sku,
                    "device": self.device_id,
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
                print(f"Successfully set color to {color} for {self.device_name}")
            else:
                print(f"Error setting color for {self.device_name}: {response.status_code}")

        if action == "brightness" and brightness:
            self.ensure_light_on()  # Ensure light is on before adjusting brightness
            payload = {
                "requestId": "unique-request-id",
                "payload": {
                    "sku": self.sku,
                    "device": self.device_id,
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
                print(f"Successfully set brightness to {brightness} for {self.device_name}")
            else:
                print(f"Error setting brightness for {self.device_name}: {response.status_code}")

    @staticmethod
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

def get_devices():
    """Retrieve all devices and their capabilities."""
    response = requests.get(
        f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error retrieving devices: {response.status_code}")
        return []

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
        if device.get('deviceName') not in ['TV', 'All', 'Lamp boi', 'Fan', 'Basic Group Control', 'Sailor moon', 'Smart Curtain Lights']:
            light = Light(device)  # Create a Light object
            if args.state == "on" or args.state == "off":
                light.control(args.state)
            elif args.state == "color":
                color = Light.get_preset_color(args.color)
                light.control(args.state, color=color)
            elif args.state == "brightness" and args.brightness:
                light.control(args.state, brightness=args.brightness)

if __name__ == "__main__":
    main()
