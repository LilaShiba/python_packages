import os
import time
import board
import busio
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# ─── ENVIRONMENT SETUP ─────────────────────────────────────────────────────────

load_dotenv()
API_KEY = os.getenv("GOVEE_API_KEY")
BASE_URL = "https://openapi.api.govee.com"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# ─── EXCLUSIONS & DEVICE MAPPING ───────────────────────────────────────────────

EXCLUDED_DEVICES = {"Smart Curtain Lights", "Sailor moon", "TV", "Fan"}

BUTTON_DEVICE_MAP: Dict[int, str] = {
    0: "tall boy",
    1: "TV lights",
    2: "bed room",
    3: "couch",
    4: "desk",
    5: "parlor floor",
    6: "kitchen",
    7: "kitchen tall boi",
    8: "Lamp boi",
    9: "All",
    10: "Basic Group Control",
}

device_states: Dict[str, bool] = {}

# ─── GOVEE DEVICE FUNCTIONS ────────────────────────────────────────────────────

def get_devices() -> List[Dict]:
    """Fetch the list of devices from the Govee API."""
    try:
        res = requests.get(f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
        return res.json().get("data", []) if res.status_code == 200 else []
    except Exception as e:
        print(f"[Error] Failed to fetch devices: {e}")
        return []

def find_device(devices: List[Dict], name: str) -> Optional[Dict]:
    """Find a device by name in the list."""
    return next((d for d in devices if d.get("deviceName") == name), None)

def toggle_device(device: Dict) -> bool:
    """Toggle a device on/off. Returns the new state (True if on)."""
    name = device.get("deviceName")
    if name in EXCLUDED_DEVICES:
        print(f"[Skip] Excluded: {name}")
        return False

    current_state = device_states.get(name, False)
    new_state = not current_state

    payload = {
        "requestId": "request-id",
        "payload": {
            "sku": device["sku"],
            "device": device["device"],
            "capability": {
                "type": "devices.capabilities.on_off",
                "instance": "powerSwitch",
                "value": 1 if new_state else 0
            }
        }
    }

    try:
        res = requests.post(f"{BASE_URL}/router/api/v1/device/control", headers=HEADERS, json=payload)
        if res.status_code == 200:
            print(f"[OK] {'On' if new_state else 'Off'}: {name}")
            device_states[name] = new_state
            return new_state
        else:
            print(f"[Fail] {res.status_code} for {name}")
    except Exception as e:
        print(f"[Error] Toggle failed for {name}: {e}")

    return current_state  # Revert to previous state if failed

# ─── GESTURE SENSOR SETUP ──────────────────────────────────────────────────────

import adafruit_apds9960.apds9960 as apds9960
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
sensor = apds9960.APDS9960(i2c)
sensor.enable_gesture = True

# ─── GROUP LIGHT CONTROL ───────────────────────────────────────────────────────

def toggle_all_devices(on: bool) -> None:
    """Turn all mapped (non-excluded) devices on or off."""
    devices = get_devices()
    for name in BUTTON_DEVICE_MAP.values():
        if name in EXCLUDED_DEVICES or name == "All":
            continue
        device = find_device(devices, name)
        if not device:
            print(f"[Error] Device not found: {name}")
            continue

        current_state = device_states.get(name, False)
        if current_state != on:
            toggle_device(device)

# ─── GESTURE LISTENER ──────────────────────────────────────────────────────────

def gesture_loop() -> None:
    """Continuously listen for up/down gestures to control lights."""
    print("[Info] Gesture control ready. Swipe up = ON, down = OFF.")
    try:
        while True:
            time.sleep(0.1)
            gesture_result = sensor.gesture()
            if gesture_result == 0x01:  # Up
                print("[Gesture] Up detected – turning all lights ON")
                toggle_all_devices(True)
            elif gesture_result == 0x02:  # Down
                print("[Gesture] Down detected – turning all lights OFF")
                toggle_all_devices(False)
    except KeyboardInterrupt:
        print("\n[Exit] Shutting down gracefully.")

# ─── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    gesture_loop()
