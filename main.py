from time import sleep
from skyfield.api import load, EarthSatellite, wgs84
from zoneinfo import ZoneInfo
import requests
import json

# Load a timescale
timescale = load.timescale()

# Get the satellite data from celestrak if it is out of date
#
# Only query if the data is > 2 hours old
# satellite_data_raw = requests.get("https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=JSON")
# with open(filename, 'wb') as fd:
#     for chunk in r.iter_content(chunk_size=128):
#         fd.write(chunk)
# satellite_data_raw = requests.get("https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=JSON")
# satellite_data = json.loads(satellite_data_raw.text)
# satellite_data = list(filter(lambda s : "NOAA-18" in s["OBJECT_NAME"], satellite_data))
#
# if len(satellite_data) == 0:
#     print("No satellites matching name filter found!")
#     exit(1)
#
# # Print the found objects by name
# for sat in satellite_data:
#     print(sat["OBJECT_NAME"])

lincoln = wgs84.latlon(+40.806862, -96.681679)

line1 = "1 90000U 25090A   25091.17708220 -.00012090  00000-0 -25444-3 0    64"
line2 = "2 90000  90.0015 318.6050 0001128  47.8434 312.3114 15.45593922    34"
satellite = EarthSatellite(line1, line2, "Fram2", timescale)
difference = satellite - lincoln

t0 = timescale.utc(2025, 3, 31, 1, 47)
t1 = t0 + 4
t, events = satellite.find_events(lincoln, t0, t1, altitude_degrees=15.0)
event_names = 'rise', 'culminate', 'set'

print("Passes starting:")
for ti, event in zip(t, events):
    if event != 0:
        continue

    name = event_names[event]
    print(ti.astimezone(ZoneInfo("America/Chicago")))



def track_realtime():
     while True:
        t = timescale.now()
        geocentric = satellite.at(t)
        lat, lon = wgs84.latlon_of(geocentric)

        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()

        print('-----')
        print('Latitude:', lat.degrees)
        print('Longitude:', lon.degrees)
        print(f"Altitude: {alt.degrees}")
        print(f"Azimuth: {az.degrees}")
        sleep(0.1)
