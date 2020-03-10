# Code to get the current weather information.

import urllib.request
import json

# Downtown San Francisco:
URL = 'https://forecast.weather.gov/MapClick.php?lat=37.775&lon=-122.418&unit=0&lg=english&FcstType=json'

# Get the current temperature outside in degrees Fahrenheit.
def get_outside_temperature():
    response = urllib.request.urlopen(URL)
    if response.status != 200:
        print("Got HTTP response %d from weather service" % response.status)
        return None

    data = json.load(response)

    return float(data["currentobservation"]["Temp"])

