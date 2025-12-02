#!/usr/bin/env python3

import os
import sys
import datetime
from typing import List, Dict, Tuple, Optional, Union
import requests
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2

# -----------------------------
# LOAD API KEYS FROM ../.env
# -----------------------------
load_dotenv()

MTA_API_KEY: Optional[str] = os.getenv("MTA_API_KEY")
MTA_BUS_API_KEY: Optional[str] = os.getenv("MTA_BUS_API_KEY")

# Default feeds
FEED_MAP: Dict[str, str] = {
    "123": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "456": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "ACE": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "BDFM": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
}

# -----------------------------
# LOCATION GROUPS
# -----------------------------

LOCATION_GROUPS: Dict[str, Union[List[str], str]] = {
    "smith": ["F22", "G35"],       # Smith–9th Street
    "bergen": ["F20", "G33"],      # Bergen St
    "court": ["233", "234"],       # Court St 2/3
    "atlantic": ["A30", "B26", "D45", "N22", "Q15", "R11"],  # Atlantic Av–Barclays Center
    "b63": "bus",
    "b65": "bus",
}

# -----------------------------
# NYC TRANSIT CLASS
# -----------------------------
class NYCTransit:
    def __init__(self) -> None:
        self.subway_key: Optional[str] = MTA_API_KEY
        self.bus_key: Optional[str] = MTA_BUS_API_KEY

    # =============================
    # SUBWAY
    # =============================
    def fetch_subway(self, station_prefix: str) -> None:
        """Fetch subway GTFS-realtime arrivals with line and direction."""
        if not self.subway_key:
            print("❌ Missing MTA_API_KEY in ../.env")
            return

        feed_url: str = self.select_feed(station_prefix)
        headers = {"x-api-key": self.subway_key}
        

        r = requests.get(feed_url, headers=headers)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)
        arrivals: List[Dict] = []

        for entity in feed.entity:
            if not entity.trip_update:
                continue
            route: str = entity.trip_update.trip.route_id
            status: str = entity.alert.header_text.translation[0].text if entity.alert.header_text.translation else "Normal"
            direction: int = entity.trip_update.trip.direction_id
            for stu in entity.trip_update.stop_time_update:
                if stu.stop_id.startswith(station_prefix):
                    if stu.arrival and stu.arrival.time:
                        arr_time = datetime.datetime.fromtimestamp(stu.arrival.time)
                        arrivals.append({
                            "time": arr_time,
                            "route": route,
                            "direction": direction,
                            "status": status
                        })

        self.pretty_print_subway(arrivals, station_prefix)

    def select_feed(self, station_prefix: str) -> str:
        """Select the correct GTFS feed based on the station prefix."""
        if station_prefix.startswith(("F", "B", "D", "M", "G")):
            return FEED_MAP["BDFM"]
        # Default feed for 1/2/3/4/5/6/A/C/E
        return FEED_MAP["123"]

    # =============================
    # BUS
    # =============================
    def fetch_bus(self, line: str) -> None:
        """Fetch MTA BusTime vehicle locations."""
        if not self.bus_key:
            print("❌ Missing MTA_BUS_API_KEY in ../.env")
            return

        url: str = f"https://bustime.mta.info/api/siri/vehicle-monitoring.json?key={self.bus_key}&LineRef=MTA%20NYCT_{line.upper()}"
        r = requests.get(url, timeout=10)
        data = r.json()
            
        try:
            vehicles: List[Dict] = (
                data["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]
                ["VehicleActivity"]
            )
        except KeyError:
            print("🚫 No buses found.")
            return

        if not vehicles:
            print("🚫 No buses currently active.")
            return

        arrivals: List[Tuple[str, str, float, float]] = []

        for v in vehicles:
            mvj = v["MonitoredVehicleJourney"]
            dest: str = mvj.get("DestinationName", "Unknown destination")
            loc: Dict = mvj.get("VehicleLocation", {})
            lat: float = loc.get("Latitude", 0.0)
            lon: float = loc.get("Longitude", 0.0)
            stop: str = data["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["VehicleActivity"][0]["MonitoredVehicleJourney"]["MonitoredCall"]["Extensions"]["Distances"].get("PresentableDistance")
            bearing: float = mvj.get("Bearing")
            arrivals.append((dest, stop, lat, lon, bearing))

        self.pretty_print_bus(arrivals, line)

    # =============================
    # LOCATION HANDLER
    # =============================
    def fetch_location(self, loc: str) -> None:
        """Fetch data based on location or bus line."""
        if loc not in LOCATION_GROUPS:
            print(f"❌ Unknown location: {loc}")
            return

        group = LOCATION_GROUPS[loc]

        if group == "bus":
            self.fetch_bus(loc)
            return

        for station in group:
            self.fetch_subway(station)

    # =============================
    # PRETTY PRINTERS
    # =============================
    def pretty_print_subway(self, arrivals: List[Dict], station_prefix: str) -> None:
        print("\n  🌙✨  LIVE SUBWAY ARRIVALS  ✨🌙")
        print(f"     station: {station_prefix}")
        print("  ---------------------------------------------")

        if not arrivals:
            print("  🚫 No trains found.")
            return

        now = datetime.datetime.now()
        arrivals.sort(key=lambda x: x["time"])

        for a in arrivals[:8]:
            mins: int = int((a["time"] - now).total_seconds() / 60)
            if mins < 0:
                continue
            status: str = a["status"]
            moon: str = "🌙" if mins <= 2 else "✨" if mins <= 5 else "💖"
            direction: str = "↑" if a["direction"] == 0 else "↓"
            print(f"   {moon} {mins:2d} min → Line {a['route']} {direction} at {a['time'].strftime('%I:%M %p')} status: {status}")

        print("  ---------------------------------------------\n")

    def pretty_print_bus(self, arrivals: List[Tuple[str, str, float, float, float]], route: str) -> None:
        print(f"\n  🚌🌙  LIVE BUS LOCATIONS for {route.upper()}  🌙🚌")
        print("  ---------------------------------------------")

        if not arrivals:
            print("  🚫 No buses found.")
            return

        for dest, stop, lat, lon, bearing in arrivals[:6]:
            print(f"   ✨  → {dest}   {stop} ({lat}, {lon} {bearing})")

        print("  ---------------------------------------------\n")

# -----------------------------
# COMMAND-LINE ENTRY
# -----------------------------
def main() -> None:
    t = NYCTransit()

    if "-l" in sys.argv:
        loc: str = sys.argv[sys.argv.index("-l") + 1].lower()
        t.fetch_location(loc)
        return

    if len(sys.argv) > 1:
        station: str = sys.argv[1].upper()
        t.fetch_subway(station)
        return

    # Default = Smith-9th St
    t.fetch_subway("F22")

if __name__ == "__main__":
    main()
