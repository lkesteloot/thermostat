import time

# sudo apt-get install python3-smbus
from smbus import SMBus

import db
import web
import thermometer
import display
import knob

HIST_LEN = 100
DB_WRITE_PERIOD = 60

# We're on /dev/i2c-1
bus = SMBus(1)

thermometer.init(bus)
display.init(bus)
knob.init()
conn = db.init()
web.init()

db_write_time = time.time()

hist = []
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
    heater_on = actual_temp < set_temp

    # Record settings to the database.
    now = time.time()
    if now - db_write_time > DB_WRITE_PERIOD:
        before = time.time()
        db.record(conn, actual_temp, set_temp, heater_on)
        db_write_time = now

    display.draw_value(bus, int(actual_temp)*100 + set_temp, heater_on)
    time.sleep(0.1)

bus.close()

