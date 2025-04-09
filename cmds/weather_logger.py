import time
import datetime
import json
from weather import fetch_weather  # Import the fetch_weather function from your weather script
import subprocess
import requests

# Log file where weather data will be stored
LOG_FILE = "weather_log.json"

def get_weather_data():
    """Fetches weather data from the weather script and captures its output."""
    try:
        # Call the fetch_weather function with the station 'KJFK'
        data = fetch_weather("KJFK")

        
        # Clean the relevant weather information to be logged
        weather_info = {
            "description": data.get('textDescription', 'Unknown'),
            "temperature": data.get('temperature', {}).get('value', 'N/A'),
            "humidity": data.get('relativeHumidity', {}).get('value', 'N/A'),
            "dewpoint": data.get('dewpoint', {}).get('value', 'N/A'),
            "windSpeed": data.get('windSpeed', {}).get('value', 'N/A'),
            "timestamp": data.get('timestamp', 'N/A')
        }

        return weather_info

    except Exception as e:
        print(f"❌ Error fetching weather data: {e}")
        return None


def log_weather():
    """Logs weather data to a file in a structured JSON format."""
    data = get_weather_data()
    print(data)
    if not data:
        return  

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weather_data": data
    }

    with open(LOG_FILE, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")  

    print("✅ Weather data logged!")


def main(interval=3600):
    """Starts logging weather data at a specified interval (in seconds)."""
    print("🌟 Starting weather logging...")

    try:
        while True:
            log_weather()
            print(f"⏳ Waiting for {interval} seconds before the next log entry.")
            time.sleep(interval)  # Wait for the specified interval (default 1 hour)
    except KeyboardInterrupt:
        print("\n⏹️ Logging stopped manually.")
        stop_logging()


def stop_logging():
    """Stops the logging process."""
    print("⚠️ Weather logging has been stopped.")


if __name__ == "__main__":
    main()  # Start the weather logging process by default
