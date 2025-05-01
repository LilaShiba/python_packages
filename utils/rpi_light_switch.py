import os
import time
import board
import busio
import requests
import random
from typing import Dict, List, Optional
from dotenv import load_dotenv
from adafruit_neotrellis.neotrellis import NeoTrellis

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

# Button index → Device name mapping
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

# Stores light on/off state
device_states: Dict[str, bool] = {}

# ─── TRELLIS INITIALIZATION ────────────────────────────────────────────────────

i2c = busio.I2C(board.SCL, board.SDA)
trellis = NeoTrellis(i2c)

for i in range(16):
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    trellis.set_callback(i, lambda e: on_button_pressed(e))
    trellis.pixels[i] = (0, 0, 0)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def show_trans_flag() -> None:
    """Display a simple trans flag pattern (blue-white-pink stripes)."""
    colors = [(91, 206, 250), (255, 255, 255), (245, 169, 184)]  # blue, white, pink
    for y in range(4):
        row_color = colors[y % 3]
        for x in range(4):
            trellis.pixels[y * 4 + x] = row_color
    time.sleep(2)
    clear_all_leds()

def clear_all_leds() -> None:
    """Turn off all Trellis LEDs."""
    for i in range(16):
        trellis.pixels[i] = (0, 0, 0)

def update_led(index: int, is_on: bool) -> None:
    """Change LED color based on light state."""
    trellis.pixels[index] = (random.randint(0,255), random.randint(0,255), random.randint(0,255)) if is_on else (0, 0, 0)

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

# ─── BUTTON HANDLER ────────────────────────────────────────────────────────────

def on_button_pressed(event) -> None:
    """Toggle light and update LED on button press."""
    index = event.number
    label = BUTTON_DEVICE_MAP.get(index)

    if not label:
        print(f"[Note] No mapping for button {index}")
        return

    devices = get_devices()
    device = find_device(devices, label)
    if not device:
        print(f"[Error] Device not found: {label}")
        return

    new_state = toggle_device(device)
    update_led(index, new_state)

# ─── MAIN LOOP ─────────────────────────────────────────────────────────────────

def main() -> None:
    """Main loop for NeoTrellis interaction."""
    show_trans_flag()
    print("[Ready] NeoTrellis initialized. Listening for input...")
    try:
        while True:
            trellis.sync()
            time.sleep(0.05)
    except KeyboardInterrupt:
        clear_all_leds()
        print("\n[Exit] Shutting down gracefully.")

# ─── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
