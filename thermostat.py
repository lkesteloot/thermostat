import time
import sys
import datetime
import dateutil.tz

# sudo apt-get install python3-smbus
from smbus import SMBus

# sudo apt-get install python3-rpi.gpio
import RPi.GPIO as GPIO

import db
import web
import thermometer
import display
import knob
import weather
import relay

HIST_LEN = 100
DB_WRITE_PERIOD = 60

# We're on /dev/i2c-1
bus = SMBus(1)

GPIO.setmode(GPIO.BOARD)
thermometer.init(bus)
display.init(bus)
knob.init()
conn = db.init()
web.init()
relay.init()

TIMEZONE = dateutil.tz.gettz('US/Pacific')

def get_is_day():
    now = datetime.datetime.now(TIMEZONE)
    return now.hour >= 8 and now.hour < 20

is_day = None
db_write_time = 0
last_heater_on = None
hist = []
heater_on = False

try:
    while True:
        # Compute actual temperature.
        f = thermometer.get_temp(bus)
        hist.append(f)
        while len(hist) > HIST_LEN:
            hist.pop(0)
        actual_temp = sum(hist) / len(hist)

        # Compute set temperature.
        new_is_day = get_is_day()
        if new_is_day != is_day:
            # Changed time block.
            is_day = new_is_day
            set_temp = 70 if is_day else 60
            sys.stderr.write("Automatic set temperature: %d\n" % set_temp)
            knob.set_temp(set_temp)

        set_temp = knob.get_temp()

        # Whether heater is on.
        heater_on = True if int(actual_temp) < int(set_temp) \
                else False if int(actual_temp) > int(set_temp) \
                else heater_on

        # For testing or emergencies.
        # heater_on = False

        # Update relay.
        if heater_on != last_heater_on:
            relay.set_relay(heater_on)
            sys.stderr.write("Heater has turned " + ("on" if heater_on else "off") + "\n")
            last_heater_on = heater_on

        # Record settings to the database.
        now = time.time()
        if now - db_write_time > DB_WRITE_PERIOD:
            before = time.time()
            outside_temp = weather.get_outside_temperature()
            db.record(conn, actual_temp, set_temp, heater_on, outside_temp)
            db_write_time = now

        display.draw_value(bus, int(actual_temp)*100 + set_temp, heater_on)
        time.sleep(0.1)
except KeyboardInterrupt:
    print()

finally:
    print("Cleaning up i2c...")
    bus.close()
    print("Cleaning up GPIO...")
    GPIO.cleanup()
    print("Done cleaning up...")
    sys.exit(0)

