import time

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

db_write_time = 0

last_heater_on = None

hist = []

try:
    while True:
        # Compute actual temperature.
        f = thermometer.get_temp(bus)
        hist.append(f)
        while len(hist) > HIST_LEN:
            hist.pop(0)
        actual_temp = sum(hist) / len(hist)

        # Compute set temperature.
        set_temp = knob.get_value()

        # Whether heater is on.
        heater_on = True if int(actual_temp) < int(set_temp) \
                else False if int(actual_temp) > int(set_temp) \
                else heater_on

        # Update relay.
        if heater_on != last_heater_on:
            relay.set_relay(heater_on)
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
    pass

print("Cleaning up...")
bus.close()
GPIO.cleanup()

