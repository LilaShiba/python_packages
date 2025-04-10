import sys
import os
import time
import csv
import datetime

# Manually adjust the Python path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules from 'cmds' folder
from cmds.pollen import Pollen
from cmds.s_array import Runner
from cmds.scan_network import ScanNetwork
from cmds.send_txt import SendTxt
from cmds.sensor_subprocess import SensorSubprocess
from cmds.single_s_array import SensorDataRecorder  # Correct import statement
from cmds.weather import Weather
from cmds.sky import Sky


class GateAdmin:
    def __init__(self, log_file="api_calls_log.csv"):
        self.pollen = Pollen()
        self.s_array = Runner()
        self.scan_network = ScanNetwork()
        self.send_txt = SendTxt()
        self.sensor_subprocess = SensorSubprocess()
        self.single_s_array = SensorDataRecorder()  # Create instance of SensorDataRecorder
        self.weather = Weather()
        self.sky = Sky()
        self.log_file = log_file
        self._initialize_log()

    def _initialize_log(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, mode='x', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['timestamp', 'api_endpoint', 'status', 'response_data'])
            except Exception as e:
                print(f"❗ Failed to create log file: {e}")

    def _log_api_call(self, endpoint, status, response_data):
        """Log an API call's details into a CSV file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, endpoint, status, response_data])
        except Exception as e:
            print(f"❗ Logging failed for {endpoint}: {e}")

    def _delay_sensor_reading(self, sensor_method):
        """Allow 10 seconds for sensors to stabilize before recording data."""
        print(f"⏳ Waiting 10 seconds for sensor '{sensor_method.__name__}' to stabilize...")
        time.sleep(10)
        return sensor_method()

    def run(self):
        """Run all the commands, ensuring sensors are delayed before reading data."""
        tasks = [
            ("Pollen", self.pollen.main, False),
            ("Weather", self.weather.main, False),
            ("SingleSArray", self.single_s_array.main, False),
            ("Sky", self.sky.main, False),
            ("ScanNetwork", self.scan_network.main, False),
        ]

        for name, method, requires_delay in tasks:
            self._log_api_call(name, "Started", "N/A")
            try:
                response = method() if not requires_delay else method()
                print(f"✅ {name} response:", response)
                self._log_api_call(name, "Completed", response)
            except Exception as e:
                error_message = f"Error in {name}: {e}"
                print(f"❌ {error_message}")
                self._log_api_call(name, "Failed", error_message)

    def start(self):
        """Start the GateAdmin system."""
        self.run()


if __name__ == "__main__":
    gate_admin = GateAdmin()
    gate_admin.start()
