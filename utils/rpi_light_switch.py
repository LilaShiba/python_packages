import os
import time
import requests
import RPi.GPIO as GPIO
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("GOVEE_API_KEY")
BASE_URL = "https://openapi.api.govee.com"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# GPIO Setup
SWITCH_PIN = 17  # Use GPIO 17 (pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def get_devices():
    """Retrieve all devices and their capabilities."""
    response = requests.get(
        f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error retrieving devices: {response.status_code}")
        return []


def control_device_power(device, action):
    """Turn the device on or off."""
    if "sku" not in device or "device" not in device or device.get('deviceName') in ['Smart Curtain Lights', 'Sailor moon', 'TV', 'Fan']:
        print(f"Skipping for {device.get('deviceName', 'unknown')}")
        return

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
        print(
            f"Successfully turned {action} {device.get('deviceName', 'unknown')}")
    else:
        print(
            f"Error turning {action} {device.get('deviceName', 'unknown')}: {response.status_code}")


def main():
    previous_state = None
    print("Monitoring switch... Press Ctrl+C to exit.")
    try:
        while True:
            # GPIO.input returns 1 if switch is up (no ground), 0 if grounded
            current_state = GPIO.input(SWITCH_PIN)
            action = "off" if current_state else "on"

            if current_state != previous_state:
                print(f"Switch changed: {'OFF' if current_state else 'ON'}")
                devices = get_devices()
                for device in devices:
                    control_device_power(device, action)
                previous_state = current_state

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
