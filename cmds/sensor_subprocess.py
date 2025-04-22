import random
import time
import subprocess
from datetime import datetime

class SensorLogger:
    """Handles the execution of the sensors command and logging the output."""
    
    def __init__(self, log_file="sensors_log.txt"):
        """Initialize the logger with a log file."""
        self.log_file = log_file

    def run_sensors(self):
        """Run the sensors command and log the output."""
        try:
            # Run the sensors command
            result = subprocess.run(['sensors'], capture_output=True, text=True)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save output to a log file
            with open(self.log_file, "a") as log:
                log.write(f"\n[{timestamp}]\n{result.stdout}\n")

            print(f"[{timestamp}] Sensors command executed.")

        except Exception as e:
            print(f"Error running sensors: {e}")

class RandomSensorRunner:
    """Randomly runs the sensors command at random intervals throughout the day."""
    
    def __init__(self, run_duration=24 * 60 * 60, min_interval=600, max_interval=7200):
        """Initialize the runner with duration and interval settings."""
        self.run_duration = run_duration  # Run for 24 hours
        self.min_interval = min_interval  # Minimum interval in seconds
        self.max_interval = max_interval  # Maximum interval in seconds
        self.sensor_logger = SensorLogger()  # Initialize the SensorLogger

    def start(self):
        """Start the random sensor runner."""
        print("Starting random sensors runner...")

        start_time = time.time()

        while time.time() - start_time < self.run_duration:
            self.sensor_logger.run_sensors()

            # Random interval between min and max interval
            interval = random.randint(self.min_interval, self.max_interval)
            print(f"Next run in {interval // 60} minutes.")
            time.sleep(interval)

class SensorSubprocess:
    def __init__(self):
        self.subprocess_number = None
    def main(self):
        """Main function to initialize and start the random sensor runner."""
        runner = RandomSensorRunner()
        runner.start()


def main():
    data = SensorSubprocess()
    return data.main()
if __name__ == "__main__":
    SensorSubprocess().main()
