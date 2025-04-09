import sys
import os
import time
import csv
import datetime

# Manually adjust the Python path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import the modules from 'cmds' folder
from cmds.pollen import Pollen
from cmds.s_array import Runner
from cmds.scan_network import ScanNetwork
from cmds.send_txt import SendTxt
from cmds.sensor_subprocess import SensorSubprocess
from cmds.single_s_array import SingleSArray
from cmds.weather import Weather
from cmds.sky import Sky


class GateAdmin:
    def __init__(self, log_file="api_calls_log.csv"):
        # Initialize each command as an instance of its respective class
        self.pollen = Pollen()
        self.s_array = Runner()
        self.scan_network = ScanNetwork()
        self.send_txt = SendTxt()
        self.sensor_subprocess = SensorSubprocess()
        self.single_s_array = SingleSArray()
        self.weather = Weather()
        self.sky = Sky()

        # Log file to record API calls
        self.log_file = log_file

        # Write CSV header if log file doesn't exist
        self._initialize_log()

    def _initialize_log(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        try:
            with open(self.log_file, mode='x', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'api_endpoint', 'status', 'response_data'])
        except FileExistsError:
            pass  # File already exists, no need to write header again

    def _log_api_call(self, endpoint, status, response_data):
        """Log an API call's details into a CSV file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, endpoint, status, response_data])

    def _delay_sensor_reading(self, sensor_method):
        """Allow 10 seconds for sensors to stabilize before recording data."""
        print(f"⏳ Waiting for 10 seconds for the sensor {sensor_method} to stabilize...")
        time.sleep(10)
        return sensor_method()

    def run(self):
        """Run all the commands, ensuring sensors are delayed by 10 seconds before recording data."""
        # Running pollen command and logging API call
        self._log_api_call('Pollen', 'Started', 'N/A')
        response = self.pollen.main()
        self._log_api_call('Pollen', 'Completed', response)

        # Running SArray command and logging API call
        self._log_api_call('SArray', 'Started', 'N/A')
        response = self.s_array.main()
        self._log_api_call('SArray', 'Completed', response)

        # Running weather command and logging API call
        self._log_api_call('Weather', 'Started', 'N/A')
        response = self.weather.main()
        self._log_api_call('Weather', 'Completed', response)

        # Running sensor subprocess with 10-second delay and logging API call
        self._log_api_call('SensorSubprocess', 'Started', 'N/A')
        response = self._delay_sensor_reading(self.sensor_subprocess.main)
        self._log_api_call('SensorSubprocess', 'Completed', response)

        # Running single SArray command with 10-second delay and logging API call
        self._log_api_call('SingleSArray', 'Started', 'N/A')
        response = self._delay_sensor_reading(self.single_s_array.main)
        self._log_api_call('SingleSArray', 'Completed', response)

        # Running Sky command and logging API call
        self._log_api_call('Sky', 'Started', 'N/A')
        response = self.sky.main()
        self._log_api_call('Sky', 'Completed', response)

        # Running scan network command and logging API call
        self._log_api_call('ScanNetwork', 'Started', 'N/A')
        response = self.scan_network.main()
        self._log_api_call('ScanNetwork', 'Completed', response)

        # Running send SMS command and logging API call
        # self._log_api_call('SendTxt', 'Started', 'N/A')
        # response = self.send_txt.main()
        # self._log_api_call('SendTxt', 'Completed', response)

    def start(self):
        """Start the GateAdmin system."""
        self.run()

if __name__ == "__main__":
    gate_admin = GateAdmin()
    gate_admin.start()
