from time import sleep
from typing import Any
from skyfield.api import load, EarthSatellite, wgs84
from zoneinfo import ZoneInfo
from rotator import Rotator

def pprint_passes(passes: list[tuple[Any, Any]]):
   i = 0
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

         print(f", {str(int(alt.degrees)):>2}°")

# Load a timescale
timescale = load.timescale()

# The position of Lincoln, NE (roughly)
lincoln = wgs84.latlon(+40.806862, -96.681679)

# Load the TLE
with open('fram2tle.txt', 'r') as f:
    lines = [line.rstrip() for line in f]
name = lines[0]
line1 = lines[1]
line2 = lines[2]
satellite = EarthSatellite(line1, line2, name, timescale)

# Calculate the "difference" between the satellite and Lincoln
difference = satellite - lincoln

# Set up and find passes for a time to 3.7 days in the future
t0 = timescale.utc(2025, 4, 1, 1, 47)
t1 = t0 + 3.7
t, events = satellite.find_events(lincoln, t0, t1, altitude_degrees=0.0)

events_zipped = list(zip(t, events))

# Pretty print the pass timings and max elevation
print("Passes starting:")
pprint_passes(events_zipped)

exit(0)

# Set up a rotator on a port
rotator = Rotator("/dev/ttyUSB0")

# Track using the rotator
while True:
   sleep(0.5)

   # Calculate the position of the satellite at the time
   t = timescale.now()
   topocentric = difference.at(t)
   alt, az, distance = topocentric.altaz()

   # Fix the azimuth to be within -180 to 180
   azimuth = az.degrees
   if azimuth > 180:
      azimuth = azimuth - 360

   print('-----')
   print(f"Altitude: {alt.degrees}")
   print(f"Azimuth: {azimuth}")

   # Do not track if the satellite is below the horizon
   if alt.degrees <= 0:
      continue

   # Send data to the rotator to track
   rotator.set_position_horizontal(-azimuth)
   rotator.set_position_vertical(alt.degrees)
