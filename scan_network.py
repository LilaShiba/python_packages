import time
import datetime
import json
import subprocess

LOG_FILE = "net.json"



def get_network_scan():
    try:
        # Run the arp-scan command and capture the output
        scan_output = subprocess.check_output(["sudo", "arp-scan", "--localnet"], stderr=subprocess.STDOUT)
        scan_output = scan_output.decode("utf-8")  # Decode bytes to string

        return scan_output

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during network scan: {e}")
        return None
    
def log_entrt(data):
    log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

    with open(LOG_FILE, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")  

    print("✅  Data logged!")

def main(interval=3600):
    """Starts logging weather data at a specified interval (in seconds)."""
    print("🌟 Starting weather logging...")

    try:
        while True:
            data = get_network_scan()
            log_entrt(data)
            time.sleep(interval)  # Wait for the specified interval (default 1 hour)
    except KeyboardInterrupt:
        print("\n⏹️ Logging stopped manually.")



if __name__ == "__main__":
    main()  # Start the weather logging process by default


