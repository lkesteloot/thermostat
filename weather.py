# Code to get the current weather information.

import urllib.request
import json
import secrets
import time

# Downtown San Francisco:
URL = 'https://forecast.weather.gov/MapClick.php?lat=37.775&lon=-122.418&unit=0&lg=english&FcstType=json'

# Get just current status.
DARK_SKY_URL = "https://api.darksky.net/forecast/" + secrets.DARK_SKY_SECRET_KEY + \
        "/" + secrets.LAT_LONG + "?exclude=minutely,hourly,daily,alerts,flags"

DARK_SKY_MAX_DAILY = 1000
DARK_SKY_MIN_PERIOD = 60*60*24/DARK_SKY_MAX_DAILY

g_last_dark_sky_temp = None
g_last_dark_sky_time = None

def _get_national_weather_service_outside_temperature():
    try:
        response = urllib.request.urlopen(URL)
        if response.status != 200:
            print("Got HTTP response %d from weather service" % response.status)
            return None

        data = json.load(response)

        return float(data["currentobservation"]["Temp"])
    except Exception as e:
        print("Got exception getting weather: %s" % e)
        return None

def _fetch_darksky_outside_temperature():
    try:
        response = urllib.request.urlopen(DARK_SKY_URL)
        if response.status != 200:
            print("Got HTTP response %d from DarkSky" % response.status)
            return None

        data = json.load(response)

        return float(data["currently"]["temperature"])
    except Exception as e:
        print("Got exception getting weather: %s" % e)
        return None

def _get_darksky_outside_temperature():
    global g_last_dark_sky_time
    global g_last_dark_sky_temp

    # Cache so we don't fetch over our quota.
    now = time.time()
    if g_last_dark_sky_temp is None or \
            g_last_dark_sky_time is None or \
            now - g_last_dark_sky_time > DARK_SKY_MIN_PERIOD:

        g_last_dark_sky_temp = _fetch_darksky_outside_temperature()
        g_last_dark_sky_time = now

    return g_last_dark_sky_temp

# Get the current temperature outside in degrees Fahrenheit.
def get_outside_temperature():
    return _get_darksky_outside_temperature()

