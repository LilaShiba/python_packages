import random
import time
import subprocess
from datetime import datetime

def run_sensors():
    """Run the sensors command and log the output."""
    try:
#        subprocess.run(['source dev/bin/activate'], capture_output=True, text=True)

        result = subprocess.run(['sensors'], capture_output=True, text=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Save output to a log file
        with open("sensors_log.txt", "a") as log:
            log.write(f"\n[{timestamp}]\n{result.stdout}\n")

        print(f"[{timestamp}] Sensors command executed.")

    except Exception as e:
        print(f"Error running sensors: {e}")

def main():
    """Randomly run the sensors command throughout the day."""
    print("Starting random sensors runner...")

    start_time = time.time()
    run_duration = 24 * 60 * 60  # Run for 24 hours

    while time.time() - start_time < run_duration:
        run_sensors()

        # Random interval between 10 minutes and 2 hours
        interval = random.randint(600, 7200)  # 600s = 10 min, 7200s = 2 hours
        print(f"Next run in {interval // 60} minutes.")
        time.sleep(interval)

if __name__ == "__main__":
    main()
