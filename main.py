from time import sleep
from skyfield.api import load, EarthSatellite, wgs84
from zoneinfo import ZoneInfo
import requests
import json

from rotator import Rotator

# Load a timescale
timescale = load.timescale()

# The position of Lincoln, NE (roughly)
lincoln = wgs84.latlon(+40.806862, -96.681679)

# Load the TLE
line1 = "1 90000U 25090A   25091.17708220 -.00012090  00000-0 -25444-3 0    64"
line2 = "2 90000  90.0015 318.6050 0001128  47.8434 312.3114 15.45593922    34"
satellite = EarthSatellite(line1, line2, "Fram2", timescale)
difference = satellite - lincoln

# Set up and find passes
# t0 = timescale.utc(2025, 4, 1, 1, 47)
# t1 = t0 + 3.7
# t, events = satellite.find_events(lincoln, t0, t1, altitude_degrees=0.0)
# event_names = 'rise', 'culminate', 'set'
#
# print("Passes starting:")
# for ti, event in zip(t, events):
#     if event != 0:
#         continue
#
#     name = event_names[event]
#     print(ti.astimezone(ZoneInfo("America/Chicago")))

new_rotator = Rotator("/dev/ttyUSB0")

while True:
   sleep(0.1)

   t = timescale.now()
   geocentric = satellite.at(t)
   lat, lon = wgs84.latlon_of(geocentric)

   topocentric = difference.at(t)
   alt, az, distance = topocentric.altaz()

   azimuth = az.degrees
   if azimuth > 180:
      azimuth = azimuth - 360

   print('-----')
   print('Latitude:', lat.degrees)
   print('Longitude:', lon.degrees)
   print(f"Altitude: {alt.degrees}")
   print(f"Azimuth: {azimuth}")

   print(new_rotator.position())

   if alt.degrees <= 0:
      continue

   new_rotator.set_position_horizontal(-azimuth)
   new_rotator.set_position_vertical(alt.degrees)
