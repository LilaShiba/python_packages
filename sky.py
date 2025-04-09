#!/usr/bin/env python3

import requests

# Define some magical Sailor Moon-themed emojis for asteroid observations
ASTEROID_EMOJIS = {
    "Observed": "🔭✨",
    "Close Approach": "🌍💫",
    "Bright": "🌟🌙",
    "Dim": "🌑💤",
    "Fast": "💨🚀",
    "Slow": "🐢🌠",
}

def get_asteroid_emoji(magnitude, velocity):
    """Assign a Sailor Moon emoji based on brightness and speed."""
    if magnitude is not None and magnitude < 15:
        emoji = ASTEROID_EMOJIS["Bright"]
    elif magnitude is not None and magnitude > 20:
        emoji = ASTEROID_EMOJIS["Dim"]
    else:
        emoji = ASTEROID_EMOJIS["Observed"]

    if velocity is not None and velocity > 10:
        emoji += " " + ASTEROID_EMOJIS["Fast"]
    elif velocity is not None and velocity < 1:
        emoji += " " + ASTEROID_EMOJIS["Slow"]

    return emoji

def fetch_nhats_data():
    """Fetch and display NHATS mission candidates."""

    url = f"https://ssd-api.jpl.nasa.gov/nhats.api?dv=6&dur=360&stay=8&launch=2020-2045&h=26&occ=7"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            return data["data"] # Limit to 5 results
        else:
            print("🌑 No NHATS mission candidates found!")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request error: {req_err}")
    
    return []

def print_asteroid_observations(observations, top_n=10):
    """Print the latest asteroid observations in a magical format."""
    print("\n🌙✨ Latest Asteroid Observations ✨🌙\n")
    
    for i, obs in enumerate(observations[:top_n], start=1):
        # Extracting relevant data with fallbacks
        designation = obs.get("des", "Unknown")
        obs_start = obs.get("obs_start", "N/A")
        obs_end = obs.get("obs_end", "N/A")
        magnitude = obs.get("obs_mag", "N/A")
        min_dv = obs.get("min_dv", {}).get("dv", "N/A")
        max_size = obs.get("max_size", "N/A")
        n_via_traj = obs.get("n_via_traj", "N/A")
        emoji = get_asteroid_emoji(magnitude, min_dv)

        # Printing the observation details
        print(f"{i}. 🪐 {designation} {emoji}")
        print(f"   📅 Observation Period: {obs_start} to {obs_end}")
        print(f"   🔆 Magnitude: {magnitude}")
        print(f"   💨 Minimum Delta-V: {min_dv} km/s")
        print(f"   🌍 Max Size: {max_size} meters")
        print(f"   🌠 Trajectory Information: {n_via_traj} possible trajectory points")
        print("   ───────────────────────────")

def get_asteroid_emoji(magnitude, min_dv):
    """Get a magical emoji based on magnitude and delta-v."""
    if magnitude is None or min_dv is None:
        return "❓"  # Unknown data
    magnitude = float(magnitude)
    min_dv = float(min_dv)
    if magnitude < 20:
        return "🌟"  # Very bright asteroid
    elif min_dv > 5:
        return "💨"  # High velocity asteroid
    else:
        return "🪐"  # Regular asteroid

def main():
    """Main function to fetch and display asteroid observations and NHATS data."""
    nhats_missions = fetch_nhats_data()

    if nhats_missions:
        print_asteroid_observations(nhats_missions)
    else:
        print("🌑 No new NHATS mission candidates available.")


if __name__ == "__main__":
    main()
