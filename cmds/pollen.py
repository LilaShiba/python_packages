#!/usr/bin/env python3

import requests
import sys
import json
from dotenv import load_dotenv
import os


class Pollen:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve the Ambee API key from the environment variable
        API_KEY = os.getenv("POLLEN")  # Ensure your actual variable name matches this
        if not API_KEY:
            print("❌ API key not found. Please add 'POLLEN' in your .env file.")
            sys.exit(1)

        self.GEO_URL = "https://nominatim.openstreetmap.org/search"
        self.POLLEN_URL = "https://api.ambeedata.com/latest/pollen/by-lat-lng"

        # Emoji dictionary for different types of allergens
        self.ALLERGEN_EMOJIS = {
            "Grass": "🌱",  # Grass pollen
            "Tree": "🌳",   # Tree pollen
            "Weed": "🌾",   # Weed pollen
        }
        self.api_key = API_KEY

    def get_coordinates(self, city_name="New York"):
        """Convert city name to coordinates using Nominatim with required User-Agent."""
        headers = {
            "User-Agent": "cli-tools/1.0 (Lila James; pollen@local.test)"  # Adding User-Agent header to avoid rate-limiting issues
        }
        params = {"q": city_name, "format": "json"}
        try:
            response = requests.get(self.GEO_URL, params=params, headers=headers)
            results = response.json()
        except Exception as e:
            print(f"❌ Failed to decode response from geocoder: {e}")
            return None, None

        if not results:
            print(f"❌ Could not find coordinates for {city_name}")
            return None, None

        return float(results[0]["lat"]), float(results[0]["lon"])

    def fetch_pollen_data(self, lat, lng):
        """Fetch pollen data from Ambee API."""
        headers = {"x-api-key": self.api_key}
        params = {"lat": lat, "lng": lng}
        try:
            response = requests.get(self.POLLEN_URL, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error fetching pollen data: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Failed to fetch pollen data: {e}")
            return {}

    def display_pollen_data(self, data, lat, lon):
        """Display pollen data in a user-friendly format with top allergens based on species."""
        pollen_info = data.get("data", [])[0] if data.get("data") else {}
        if not pollen_info:
            print("❌ No pollen data available.")
            return

        updated_at = pollen_info.get('updatedAt', 'N/A')

        # Getting the species counts for each type
        species = pollen_info.get("Species", {})
        risk = pollen_info.get("Risk", {})
        counts = pollen_info.get("Count", {})

        print(f"\n📍 Location: Latitude {lat}, Longitude {lon}")
        print(f"📅 Date: {updated_at}")
        print("\n🌿 Top Allergens:")

        # Process Grass, Tree, and Weed species and display the top 2 allergens
        for category, allergens in species.items():
            print(f"\n🔖 {category}:")
            
            if isinstance(allergens, dict):
                # Sort allergens by count and get top 2
                sorted_allergens = sorted(allergens.items(), key=lambda x: x[1], reverse=True)[:2]
                
                for allergen, count in sorted_allergens:
                    emoji = self.ALLERGEN_EMOJIS.get(category, "❓")
                    risk_level = risk.get(f"{category.lower()}_pollen", "N/A")
                    print(f"   {emoji} {allergen}: {count} grains/m³ (Risk: {risk_level})")
            
            else:
                emoji = self.ALLERGEN_EMOJIS.get(category, "❓")
                risk_level = risk.get(f"{category.lower()}_pollen", "N/A")
                print(f"   {emoji} {category}: {allergens} grains/m³ (Risk: {risk_level})")
        return data
    
    def run(self, city="New York"):
        lat, lng = self.get_coordinates(city)
        if lat is not None and lng is not None:
            data = self.fetch_pollen_data(lat, lng)
            self.display_pollen_data(data, lat, lng)
    
def main():
    if len(sys.argv) <= 1:
        print("Usage: pollen <City Name> (defaults to New York if no city is provided)")
        city = "New York"
    else:
        city = " ".join(sys.argv[1:])

    pollen = Pollen()
    return pollen.run(city)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    p = Pollen()
    p.main()
