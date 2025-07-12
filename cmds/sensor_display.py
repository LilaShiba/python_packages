import os
import time
import board
import busio
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# ─── I2C DEVICES ───────────────────────────────────────────────────────────────
from adafruit_ht16k33.segments import Seg14x4
import adafruit_bme680
from adafruit_apds9960.apds9960 import APDS9960

i2c = busio.I2C(board.SCL, board.SDA)

# Initialize sensors
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
apds = APDS9960(i2c)
apds.enable_color = True
apds.enable_proximity = True
apds.enable_gesture = True
# Initialize display
display = Seg14x4(i2c, address=0x70)
display.fill(0)
# ─── ENVIRONMENT SETUP ─────────────────────────────────────────────────────────

load_dotenv()
API_KEY = os.getenv("GOVEE_API_KEY")
BASE_URL = "https://openapi.api.govee.com"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# ─── DEVICE MAPPING ────────────────────────────────────────────────────────────

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

# ─── SAFE HELPERS ──────────────────────────────────────────────────────────────

def safe_call(sensor_func, fallback=None, label="sensor"):
    try:
        return sensor_func()
    except (OSError, IOError) as e:
        print(f"[Warning] {label} read failed: {e}")
        return fallback

def format_and_display(display, label: str, value, unit: str):
    if value is None:
        msg = f"{label}: N/A"
    else:
        msg = f"{label} {value:.1f} {unit}"
    display.marquee(msg + "    ", loop=False, delay=0.4)

# ─── GOVEE API ─────────────────────────────────────────────────────────────────

def get_devices() -> List[Dict]:
    try:
        res = requests.get(f"{BASE_URL}/router/api/v1/user/devices", headers=HEADERS)
        return res.json().get("data", []) if res.status_code == 200 else []
    except Exception as e:
        print(f"[Error] Failed to fetch devices: {e}")
        return []

def find_device(devices: List[Dict], name: str) -> Optional[Dict]:
    return next((d for d in devices if d.get("deviceName") == name), None)

def toggle_device(device: Dict, on: Optional[bool] = None) -> bool:
    name = device.get("deviceName")
    if name in EXCLUDED_DEVICES:
        print(f"[Skip] Excluded: {name}")
        return False

    current_state = device_states.get(name, False)
    new_state = on if on is not None else not current_state

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

    return current_state

def toggle_all_devices(on: bool) -> None:
    devices = get_devices()
    for name in BUTTON_DEVICE_MAP.values():
        if name in EXCLUDED_DEVICES or name == "All":
            continue
        device = find_device(devices, name)
        if device:
            toggle_device(device, on=on)
            
def gesture_check():
       # ─── Gesture Check ─────────────────────────────────────
    gesture = apds.gesture()
    if gesture == 0x01:
        print("[Gesture] Up → All lights ON")
        toggle_all_devices(True)
    elif gesture == 0x02:
        print("[Gesture] Down → All lights OFF")
        toggle_all_devices(False)

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():


    print("[Start] Gesture + Sensor display loop. Swipe up = ON, down = OFF.")

    try:
        while True:
            # ─── Sensor Readout ─────────────────────────────────────
            temperature = safe_call(lambda: bme680.temperature, label="Temperature")
            gas = safe_call(lambda: bme680.gas, label="Gas")
            pressure = safe_call(lambda: bme680.pressure, label="Pressure")
            humidity = safe_call(lambda: bme680.humidity, label="Humidity")
            color_data = safe_call(lambda: apds.color_data, label="Light")
            gesture_check()
            # ─── Display Info ──────────────────────────────────────
            format_and_display(display, "temp", temperature, "C")
            time.sleep(2)
            gesture_check()
            if temperature is not None:
                format_and_display(display, "temp", ((9/5)*temperature)+32, "F")
            else:
                format_and_display(display, "temp", None, "F")
            time.sleep(2)
            gesture_check()
            format_and_display(display, "gas", gas, "k")
            gesture_check()
            time.sleep(2)
            format_and_display(display, "p", pressure, "h")
            gesture_check()

            time.sleep(2)
            gesture_check()

            format_and_display(display, "h", humidity, "%")
            time.sleep(2)
            gesture_check()

            # format_and_display(display, "light", color_data, "lux")
            # time.sleep(2)
            format_and_display(display, "stay magical cunt", 420 ,"\_ ^_^)_/")
            time.sleep(2)
            gesture_check()


     

    except KeyboardInterrupt:
        display.fill(0)
        print("[Exit] Program terminated by user.")

# ─── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
