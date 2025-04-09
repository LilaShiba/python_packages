import time
import datetime
import json
import subprocess

class NetworkLogger:
    """Class for performing network scans and logging the results to a file."""

    LOG_FILE = "net.json"

    def __init__(self, interval=3600):
        """Initialize the NetworkLogger with a logging interval (default 1 hour)."""
        self.interval = interval

    def get_network_scan(self):
        """Run a network scan using arp-scan and return the output."""
        try:
            # Run the arp-scan command and capture the output
            scan_output = subprocess.check_output(["sudo", "arp-scan", "--localnet"], stderr=subprocess.STDOUT)
            scan_output = scan_output.decode("utf-8")  # Decode bytes to string
            return scan_output

        except subprocess.CalledProcessError as e:
            print(f"❌ Error during network scan: {e}")
            return None

    def log_entry(self, data):
        """Log the network scan data with a timestamp to the log file."""
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

        with open(self.LOG_FILE, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

        print("✅  Data logged!")

    def start_logging(self):
        """Starts logging network data at the specified interval."""
        print("🌟 Starting network logging...")

        try:
            while True:
                data = self.get_network_scan()
                if data:
                    self.log_entry(data)
                time.sleep(self.interval)  # Wait for the specified interval
        except KeyboardInterrupt:
            print("\n⏹️ Logging stopped manually.")

class ScanNetwork:
    def __init__(self):
        pass

    def main(self):
        """Main function to start the network logging process."""
        logger = NetworkLogger(interval=3600)  # Default interval of 1 hour
        logger.start_logging()

if __name__ == "__main__":
    ScanNetwork().main()
