import time
import datetime
import json
import subprocess
from pathlib import Path


class NetworkLogger:
    LOG_FILE = Path("net_scans.json")

    def __init__(self, interval=3600):
        self.interval = interval
        self.interface = "en0"  # or autodetect if you want

    @staticmethod
    def now():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def pretty(msg, icon="📘"):
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} {icon} {msg}")

    # ---------------------------------------------------------
    # Parse arp-scan output into structured device objects
    # ---------------------------------------------------------
    def parse_scan(self, raw):
        devices = []
        for line in raw.splitlines():
            # Typical line:
            # 10.0.0.12    dc:aa:11:aa:bb:cc    Apple, Inc.
            parts = line.split("\t")
            if len(parts) < 3:
                continue

            ip = parts[0].strip()
            mac = parts[1].strip()
            vendor = parts[2].strip()

            # skip headers or garbage
            if not mac or mac == "(Unknown)":
                continue

            devices.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor
            })

        return devices

    # ---------------------------------------------------------
    def get_scan(self):
        try:
            result = subprocess.run(
                ["sudo", "arp-scan", "--interface", self.interface, "--localnet"],
                capture_output=True,
                text=True
            )
            if result.returncode not in [0, 1]:
                self.pretty(f"arp-scan failed ({result.returncode})", "❌")
                return None

            return result.stdout

        except Exception as e:
            self.pretty(f"Exception: {e}", "💥")
            return None

    # ---------------------------------------------------------
    def log_entry(self, devices):
        entry = {
            "timestamp": self.now(),
            "interface": self.interface,
            "device_count": len(devices),
            "devices": devices
        }

        with self.LOG_FILE.open("a") as f:
            json.dump(entry, f)
            f.write("\n")  # JSON Lines

        self.pretty(f"Logged {len(devices)} devices.", "💾")

    # ---------------------------------------------------------
    def start(self):
        self.pretty(f"Starting logging on {self.interface}…", "🌟")

        try:
            while True:
                raw = self.get_scan()
                if raw:
                    devices = self.parse_scan(raw)
                    self.log_entry(devices)
                else:
                    self.pretty("No scan data.", "⚠️")

                self.pretty(f"Sleeping {self.interval}s", "😴")
                time.sleep(self.interval)

        except KeyboardInterrupt:
                self.pretty("Stopped.", "⏹️")

    # --------------------------------------------------------------------------
def main():
    logger = NetworkLogger(interval=3600)
    logger.start()


if __name__ == "__main__":
    self.main()
