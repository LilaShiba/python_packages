import csv
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Raspberry Pi-specific imports
import board
import busio

# Adafruit sensors
import adafruit_lsm9ds1
import adafruit_apds9960.apds9960
import adafruit_bme680
import adafruit_gps

# Constants
I2C_FREQUENCY = 1  # Hz
MAX_RETRIES = 5
RETRY_DELAY = 0.5


# 🛠️ Initialization Functions
def init_i2c() -> busio.I2C:
    """Initializes and returns the I2C connection."""
    return busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQUENCY)


def init_sensors(i2c: busio.I2C) -> dict:
    """Initializes all sensors and returns them as a dictionary."""
    return {
        "lsm9ds1": adafruit_lsm9ds1.LSM9DS1_I2C(i2c),
        "apds9960": adafruit_apds9960.apds9960.APDS9960(i2c),
        "bme680": adafruit_bme680.Adafruit_BME680_I2C(i2c),
        "gps": adafruit_gps.GPS_GtopI2C(i2c, debug=False)
    }


def configure_sensors(sensors: dict) -> None:
    """Configures sensor settings."""
    sensors["apds9960"].enable_proximity = True
    sensors["apds9960"].enable_color = True


# 🔥 Sensor Reading Functions with Error Handling
def safe_read(func, retries=MAX_RETRIES) -> Optional[Tuple]:
    """Safely read sensor data with retries and graceful error handling."""
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            print(f"⚠️ Error reading sensor: {e} (Attempt {attempt}/{retries})")
            time.sleep(RETRY_DELAY)
    print("❌ Failed to read sensor data after retries.")
    return None


def read_lsm9ds1(sensor) -> Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float], float]]:
    """Reads LSM9DS1 acceleration, gyroscope, magnetometer, and temperature with map conversion."""
    result = safe_read(lambda: (
        tuple(sensor.acceleration),   # Convert map to tuple
        tuple(sensor.gyro),           # Convert map to tuple
        tuple(sensor.magnetic),       # Convert map to tuple
        sensor.temperature
    ))
    return result


def read_apds9960(sensor) -> Optional[Tuple[int, Tuple[int, int, int, int], int]]:
    """Reads proximity and color data from the APDS9960 sensor with map conversion."""
    result = safe_read(lambda: (
        sensor.proximity,
        tuple(sensor.color_data),     # Convert map to tuple
        sum(sensor.color_data)
    ))
    return result


def read_bme680(sensor) -> Optional[Tuple[float, float, float, float]]:
    """Reads temperature, gas resistance, humidity, and pressure with error handling."""
    return safe_read(lambda: (
        sensor.temperature,
        sensor.gas,
        sensor.humidity,
        sensor.pressure
    ))


def read_gps(gps) -> Optional[Tuple[float, float, float]]:
    """Reads data from the GPS module with error handling."""
    def get_gps_data():
        gps.update()
        return gps.latitude, gps.longitude, gps.speed_knots

    return safe_read(get_gps_data)


# 📊 Data Recording with Error Handling
def record_data(csv_path: str, sensors: dict, duration: int, frequency: int = 1) -> None:
    """Records sensor data to a CSV file with error handling."""
    end_time = datetime.now() + timedelta(seconds=duration)

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Timestamp', 'Accel_X', 'Accel_Y', 'Accel_Z',
            'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z',
            'Temp_LSM9DS1', 'Proximity', 'Color_R', 'Color_G', 'Color_B', 'Color_C',
            'BME680_Temp', 'Gas', 'Humidity', 'Pressure',
            'GPS_Latitude', 'GPS_Longitude', 'GPS_Speed'
        ])

        while datetime.now() < end_time:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            # Safely read sensor data
            lsm_data = read_lsm9ds1(sensors['lsm9ds1'])
            apds_data = read_apds9960(sensors['apds9960'])
            bme_data = read_bme680(sensors['bme680'])
            gps_data = read_gps(sensors['gps'])

            # Handle missing data with placeholders
            accel, gyro, mag, temp = lsm_data or ((0, 0, 0), (0, 0, 0), (0, 0, 0), 0)
            prox, color, lux = apds_data or (0, (0, 0, 0, 0), 0)
            bme_temp, gas, humidity, pressure = bme_data or (0, 0, 0, 0)
            lat, lon, speed = gps_data or (None, None, None)

            # Write data to CSV
            writer.writerow([
                timestamp, *accel, *gyro, *mag, temp,
                prox, *color, bme_temp, gas, humidity, pressure,
                lat, lon, speed
            ])

            # Print sensor data for debugging
            print(f"Timestamp: {timestamp}")
            print(f"Accel: {accel}, Gyro: {gyro}, Mag: {mag}, Temp: {temp}")
            print(f"Proximity: {prox}, Color: {color}, Lux: {lux}")
            print(f"BME680 Temp: {bme_temp}, Gas: {gas}, Humidity: {humidity}, Pressure: {pressure}")
            print(f"GPS Latitude: {lat}, Longitude: {lon}, Speed: {speed}")
            print("-" * 40)

            time.sleep(1 / frequency)


# 🚀 Main Execution
def main():
    try:
        i2c = init_i2c()
        sensors = init_sensors(i2c)
        configure_sensors(sensors)

        csv_path = f"data/sensor_data_{datetime.now().strftime('%Y-%m-%dT%H:%M')}.csv"
        print("Starting data recording...")
        record_data(csv_path, sensors, duration=360, frequency=1)

        print(f"✅ Data saved to {csv_path}")

    except Exception as e:
        print(f"🔥 Fatal error: {e}")


if __name__ == "__main__":
    main()
