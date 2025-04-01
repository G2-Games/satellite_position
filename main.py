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
line1 = "1 63427U 25066A   25091.13562238  .00000291 -92113-6  00000+0 0  9992"
line2 = "2 63427  90.0051 318.4936 0157861  92.0495  34.6835 15.88239845    02"
satellite = EarthSatellite(line1, line2, "Fram2", timescale)
difference = satellite - lincoln

# Set up and find passes
t0 = timescale.utc(2025, 4, 1, 1, 47)
t1 = t0 + 3.7
t, events = satellite.find_events(lincoln, t0, t1, altitude_degrees=0.0)
event_names = 'rise', 'culminate', 'set'

events_zipped = list(zip(t, events))
i = 0

print("Passes starting:")
while i < len(events_zipped):
   event = events_zipped[i]
   i += 1

   if event[1] != 0:
      continue

   print(event[0].astimezone(ZoneInfo("America/Chicago")).strftime('%a %d, %I:%M %p'), end="")

   if events_zipped[i][1] == 1:
      t = events_zipped[i][0]
      topocentric = difference.at(t)
      alt, az, distance = topocentric.altaz()

      azimuth = az.degrees
      if azimuth > 180:
         azimuth = azimuth - 360

      print(f", {str(int(alt.degrees)):>2}° {str(int(az.degrees)):>3}°")

exit(0)

new_rotator = Rotator("/dev/ttyUSB0")

while True:
   sleep(0.5)

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
