#!/usr/bin/env python3

import requests
import sys

API_HEADERS = {"User-Agent": "WeatherCLI (your.email@example.com)"}

WEATHER_EMOJIS = {
    "Clear": "🌙✨", "Sunny": "☀️🌞", "Mostly Sunny": "🌤️✨", "Partly Cloudy": "⛅🌙", "Cloudy": "☁️🌫️", "Overcast": "🌥️💜",
    "Haze": "🌫️💨", "Mist": "🌫️✨", "Fog": "🌫️👀", "Dense Fog": "🌫️🌀",
    "Drizzle": "🌦️💖", "Light Rain": "🌦️💙", "Rain": "🌧️💙", "Heavy Rain": "🌧️🌊", "Showers": "🌦️🌊", 
    "Thunderstorm": "⛈️⚡", "Severe Thunderstorm": "⛈️🔥", "Lightning": "⚡🌩️",
    "Snow": "❄️☃️", "Light Snow": "🌨️❄️", "Heavy Snow": "❄️🌨️❄️", "Snow Showers": "🌨️🌬️", "Blizzard": "🌨️💨❄️",
    "Sleet": "🌧️❄️", "Freezing Rain": "🌧️❄️🔥",
    "Windy": "💨🌪️", "Strong Winds": "💨💥", "Hurricane": "🌀🌪️💀", "Tornado": "🌪️😱",
    "Smoke": "🔥🌫️", "Dust": "🌫️🏜️", "Sandstorm": "🏜️💨", "Ash": "🌋🌫️",
}

def get_emoji(description):
    """Match weather descriptions to magical emojis."""
    return next((emoji for key, emoji in WEATHER_EMOJIS.items() if key.lower() in description.lower()), "🌙🌌")

def fetch_weather(station):
    """Fetch and display current weather from NOAA API."""
    try:
        url = f"https://api.weather.gov/stations/{station}/observations/latest"
        data = requests.get(url, headers=API_HEADERS).json().get("properties", {})

        description = data.get('textDescription', 'Unknown')
        temp = data.get('temperature', {}).get('value', 'N/A')
        emoji = get_emoji(description)

        print("\n🌙✨ Magic Weather Report ✨🌙\n")
        print(f"📍  Station: {station}")
        print(f"⏳  Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"🌤️  Weather: {description} {emoji}")
        print(f"🔥  Temperature: {temp} °C")
        print(f"🔥  F: {(temp * 9/5) + 32:.1f} °F" if temp != 'N/A' else "🔥  Temperature: N/A")

        print(f"💦  Dewpoint: {data.get('dewpoint', {}).get('value', 'N/A')}°C")
        print(f"💨  Wind Speed: {data.get('windSpeed', {}).get('value', 'N/A')} km/h")
        print(f"🧭  Wind Direction: {data.get('windDirection', {}).get('value', 'N/A')}°")
        print(f"💧  Humidity: {data.get('relativeHumidity', {}).get('value', 'N/A')}%")
        print(f"⚖️   Pressure: {data.get('barometricPressure', {}).get('value', 'N/A')} Pa")
        print("\n🌟 Stay magical! 🌟\n")
        return data

    except Exception as e:
        print(f"❌ Error fetching weather data: {e}")

def fetch_forecast(station):
    """Fetch and display 3-day forecast."""
    try:
        # Get coordinates
        url = f"https://api.weather.gov/stations/{station}"
        coords = requests.get(url, headers=API_HEADERS).json()["geometry"]["coordinates"]
        lat, lon = coords[1], coords[0]

        # Get forecast URL
        forecast_url = requests.get(f"https://api.weather.gov/points/{lat},{lon}", headers=API_HEADERS).json()["properties"]["forecast"]
        periods = requests.get(forecast_url, headers=API_HEADERS).json()["properties"]["periods"][:6]

        print(f"\n🔮✨ 3-Day Forecast for {station} ✨🔮")
        for p in periods:
            print(f"📅 {p['name']}: {p['shortForecast']} {get_emoji(p['shortForecast'])} | {p['temperature']}°{p['temperatureUnit']}")

    except Exception as e:
        print(f"❌ Error fetching forecast data: {e}")

class Weather:
    def __init__(self):
        self.process_id = None
    def main(self):
        """Parse input and call weather functions."""
        args = sys.argv[1:] if len(sys.argv) > 2 else "KJFK"
        if not args:
            print("Usage: weather [-future] STATION")
            sys.exit(1)

        future = "-future" in args
        station = next((arg for arg in args if not arg.startswith("-")), "KJFK")

        fetch_forecast(station) if future else fetch_weather(station)

if __name__ == "__main__":
    Weather().main()
