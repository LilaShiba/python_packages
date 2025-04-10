import csv
import time
import os
import argparse
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
class SensorInitializer:
    """Handles the initialization of I2C and sensors."""
    
    def __init__(self, frequency: int = I2C_FREQUENCY):
        self.i2c = self.init_i2c(frequency)
        self.sensors = self.init_sensors()

    def init_i2c(self, frequency: int) -> busio.I2C:
        """Initializes and returns the I2C connection."""
        return busio.I2C(board.SCL, board.SDA, frequency=frequency)

    def init_sensors(self) -> dict:
        """Initializes all sensors and returns them as a dictionary."""
        return {
            "lsm9ds1": adafruit_lsm9ds1.LSM9DS1_I2C(self.i2c),
            "apds9960": adafruit_apds9960.apds9960.APDS9960(self.i2c),
            "bme680": adafruit_bme680.Adafruit_BME680_I2C(self.i2c),
            "gps": adafruit_gps.GPS_GtopI2C(self.i2c, debug=False)
        }

    def configure_sensors(self) -> None:
        """Configures sensor settings."""
        self.sensors["apds9960"].enable_proximity = True
        self.sensors["apds9960"].enable_color = True


# 🧱 Helpers
class FileHelper:
    """Handles file operations like ensuring the data folder exists."""
    
    @staticmethod
    def ensure_data_folder(path: str) -> None:
        """Ensures the directory for the given path exists."""
        os.makedirs(os.path.dirname(path), exist_ok=True)


# 🔥 Sensor Reading Functions with Error Handling
class SensorReader:
    """Handles the safe reading of sensor data."""
    
    @staticmethod
    def safe_read(func, retries=MAX_RETRIES) -> Optional[Tuple]:
        """Safely read sensor data with retries and graceful error handling."""
        for attempt in range(1, retries + 1):
            try:
                return func()
            except Exception as e:
                print(
                    f"⚠️ Error reading sensor: {e} (Attempt {attempt}/{retries})")
                time.sleep(RETRY_DELAY)
        print("❌ Failed to read sensor data after retries.")
        return None

    @staticmethod
    def read_lsm9ds1(sensor) -> Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float], float]]:
        return SensorReader.safe_read(lambda: (
            tuple(sensor.acceleration),
            tuple(sensor.gyro),
            tuple(sensor.magnetic),
            sensor.temperature
        ))

    @staticmethod
    def read_apds9960(sensor) -> Optional[Tuple[int, Tuple[int, int, int, int], int]]:
        return SensorReader.safe_read(lambda: (
            sensor.proximity,
            tuple(sensor.color_data),
            sum(sensor.color_data)
        ))

    @staticmethod
    def read_bme680(sensor) -> Optional[Tuple[float, float, float, float]]:
        return SensorReader.safe_read(lambda: (
            sensor.temperature,
            sensor.gas,
            sensor.humidity,
            sensor.pressure
        ))

    @staticmethod
    def read_gps(gps) -> Optional[Tuple[float, float, float]]:
        def get_gps_data():
            gps.update()
            return gps.latitude, gps.longitude, gps.speed_knots
        return SensorReader.safe_read(get_gps_data)


# 📊 Data Recording with Error Handling
class DataRecorder:
    """Handles the recording of sensor data to CSV files."""
    
    def __init__(self, csv_path: str, sensors: dict, duration: int, frequency: int = 1):
        self.csv_path = csv_path
        self.sensors = sensors
        self.duration = duration
        self.frequency = frequency

    def record_data(self) -> None:
        """Records sensor data to a CSV file with error handling."""
        FileHelper.ensure_data_folder(self.csv_path)
        end_time = datetime.now() + timedelta(seconds=self.duration)
        print(f"📁 Writing CSV to: {self.csv_path}")
        print(f"⏳ Recording for {self.duration} seconds at {self.frequency} Hz...\n")

        with open(self.csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Timestamp', 'Accel_X', 'Accel_Y', 'Accel_Z',
                'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z',
                'Temp_LSM9DS1', 'Proximity', 'Color_R', 'Color_G', 'Color_B', 'Color_C',
                'BME680_Temp', 'Gas', 'Humidity', 'Pressure',
                'GPS_Latitude', 'GPS_Longitude', 'GPS_Speed'
            ])

            while self.duration > 0:
                self.duration -= 1
                timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

                # Sensor reads with default fallback values
                lsm_data = SensorReader.read_lsm9ds1(self.sensors['lsm9ds1'])
                apds_data = SensorReader.read_apds9960(self.sensors['apds9960'])
                bme_data = SensorReader.read_bme680(self.sensors['bme680'])
                gps_data = SensorReader.read_gps(self.sensors['gps'])

                accel, gyro, mag, temp = lsm_data or (
                    (0, 0, 0), (0, 0, 0), (0, 0, 0), 0)
                prox, color, lux = apds_data or (0, (0, 0, 0, 0), 0)
                bme_temp, gas, humidity, pressure = bme_data or (0, 0, 0, 0)
                lat, lon, speed = gps_data or (None, None, None)

                # Writing row
                writer.writerow([
                    timestamp, *accel, *gyro, *mag, temp,
                    prox, *color, bme_temp, gas, humidity, pressure,
                    lat, lon, speed
                ])

                # ✨ Verbose printout per loop (including pressure and humidity)
                print(f"\n[{timestamp}]")
                print(f"  📈 Accel:     X: {accel[0]} Y: {accel[1]} Z: {accel[2]}")
                print(f"  🔄 Gyro:      X: {gyro[0]} Y: {gyro[1]} Z: {gyro[2]}")
                print(f"  🧭 Mag:       X: {mag[0]} Y: {mag[1]} Z: {mag[2]}")
                print(f"  🌡️ LSM Temp: {temp}°C")
                print(
                    f"  🔦 Prox:      {prox} | Color: R{color[0]} G{color[1]} B{color[2]} C{color[3]}")
                print(
                    f"  🌫️ BME680:    Temp: {bme_temp}°C  Gas: {gas}Ω  Humidity: {humidity}%  Pressure: {pressure} hPa")
                print(
                    f"  📍 GPS:       Lat: {lat}  Lon: {lon}  Speed: {speed} km/h")

                time.sleep(1 / self.frequency)


# 🚀 Main Execution
class SensorDataRecorder:
    """Handles the full workflow of sensor data recording."""
    
    @staticmethod
    def main():
        args = SensorDataRecorder.parse_args()
        try:
            sensor_initializer = SensorInitializer()
            sensor_initializer.configure_sensors()

            csv_path = f"data/sensor_data_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.csv"
            print(f"📂 Saving data to: {csv_path}")
            print("📡 Starting sensor read loop...")

            data_recorder = DataRecorder(
                csv_path=csv_path,
                sensors=sensor_initializer.sensors,
                duration=args.duration,
                frequency=args.frequency
            )
            data_recorder.record_data()
            print("✅ Data recording complete!")

        except KeyboardInterrupt:
            print("\n🛑 Data recording interrupted by user.")

        except Exception as e:
            print(f"🔥 Fatal error: {e}")

    @staticmethod
    def parse_args():
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description="Record sensor data to CSV.")
        parser.add_argument('--duration', type=int, default=10,
                            help='Recording duration in seconds')
        parser.add_argument('--frequency', type=int, default=1,
                            help='Sampling frequency in Hz')
        return parser.parse_args()


if __name__ == "__main__":
    SensorDataRecorder.main()
