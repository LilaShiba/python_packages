#!/usr/bin/env python3

import requests
import re

# Fetching Sentry data
def fetch_sentry_data():
    url = "https://ssd-api.jpl.nasa.gov/sentry.api"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Sentry data: {e}")
        return []

# Helper to extract the earliest year from the risk period range
def extract_earliest_year(risk_range):
    try:
        match = re.match(r"(\d{4})", risk_range)
        return int(match.group(1)) if match else 9999
    except:
        return 9999

# Get top asteroids with highest impact probability and earliest risk year
def get_top_risk_asteroids(data, top_n=5):
    asteroids = []
    for entry in data:
        try:
            impact_probability = float(entry.get("ip", -1))
            risk_range = entry.get("range", "N/A")
            asteroid = {
                "id": entry.get("id", "N/A"),
                "designation": entry.get("des", "N/A"),
                "name": entry.get("fullname", "N/A"),
                "last_observed": entry.get("last_obs", "N/A"),
                "diameter_km": entry.get("diameter", "N/A"),
                "velocity_km_s": entry.get("v_inf", "N/A"),
                "impact_probability": impact_probability,
                "risk_period": risk_range,
                "earliest_year": extract_earliest_year(risk_range)
            }
            asteroids.append(asteroid)
        except ValueError:
            continue
    
    # Sort: highest probability first, then earliest risk year
    asteroids.sort(
        key=lambda x: (-x["impact_probability"], x["earliest_year"])
    )
    return asteroids[:top_n]

# Print the top asteroids
def print_asteroids(asteroids):
    print("\n🚀🌑 Top Potential Impact Asteroids (Ranked by Probability + Earliest Threat Year)\n")
    for i, asteroid in enumerate(asteroids, start=1):
        print(f"{i}. 🪐 {asteroid['name']} ({asteroid['designation']})")
        print(f"   📌 ID: {asteroid['id']}")
        print(f"   📅 Last Observed: {asteroid['last_observed']}")
        print(f"   🔭 Diameter: {asteroid['diameter_km']} km")
        print(f"   💨 Velocity: {asteroid['velocity_km_s']} km/s")
        print(f"   🎯 Impact Probability: {asteroid['impact_probability']}")
        print(f"   🌍 Risk Period: {asteroid['risk_period']}")
        print("   ───────────────────────────")

# Main function
def main():
    print("🌟 Fetching the latest asteroid risk data from NASA... 🌟")
    data = fetch_sentry_data()
    if data:
        top_asteroids = get_top_risk_asteroids(data)
        print_asteroids(top_asteroids)
    else:
        print("❌ No asteroid data available!")

if __name__ == "__main__":
    main()
