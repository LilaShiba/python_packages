import time
import datetime
import json
import subprocess


class NetworkLogger:
    LOG_FILE = "net.json"

    def __init__(self, interval=3600):
        self.interval = interval

    def get_network_scan(self):
        try:
            result = subprocess.run(
                ["sudo", "arp-scan", "--localnet"],
                capture_output=True,
                text=True
            )
            if result.stderr:
                print(f"⚠️ arp-scan stderr: {result.stderr.strip()}")

            if result.returncode in [0, 1]:
                return result.stdout
            else:
                print(f"❌ arp-scan failed with exit code {result.returncode}")
                return None
        except Exception as e:
            print(f"❌ Exception running arp-scan: {e}")
            return None

    def log_entry(self, data):
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

        with open(self.LOG_FILE, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

        print("✅ Data logged!")

    def start_logging(self):
        print("🌟 Starting network logging...")
        try:
            while True:
                data = self.get_network_scan()
                if data:
                    self.log_entry(data)
                else:
                    print("⚠️ No data to log this interval.")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n⏹️ Logging stopped manually.")


def main():
    logger = NetworkLogger(interval=3600)  # Default 1 hour interval
    logger.start_logging()


if __name__ == "__main__":
    main()
