import sys
import time

# sudo apt-get install sqlite3
import sqlite3

# sudo apt-get install python3-rpi.gpio
import RPi.GPIO as GPIO

# sudo apt-get install python3-smbus
from smbus import SMBus

HIST_LEN = 100

MIN_TEMP = 60
MAX_TEMP = 90
DB_WRITE_PERIOD = 60

HT16K33_DISPLAY_OFF = 0x80
HT16K33_DISPLAY_ON = 0x81
HT16K33_BRIGHTNESS = 0xE0
HT16K33_OSCILLATOR_ON = 0x21
POS = [0, 2, 6, 8]

ROT_A_PIN = 16
ROT_B_PIN = 18

# Default addresses if you don't mess with address pins.
THERMOMETER_ADDRESS = 0x18
SEVEN_SEGMENT_ADDRESS = 0x70

NUMBERS = [
    0x3F, # 0
    0x06, # 1
    0x5B, # 2
    0x4F, # 3
    0x66, # 4
    0x6D, # 5
    0x7D, # 6
    0x07, # 7
    0x7F, # 8
    0x6F, # 9
]

# Query helpers.

def query(conn, cmd, *parameters):
    return list(conn.execute(cmd, *parameters))

def query_single_row(conn, cmd, *parameters):
    rows = query(conn, cmd, *parameters)
    return rows[0] if rows else None

def query_single_value(conn, cmd, *parameters):
    row = query_single_row(conn, cmd, *parameters)
    return row[0] if row is not None else None

def db_upgrade0(conn):
	conn.execute('''CREATE TABLE temp (
		id INTEGER PRIMARY KEY,
		actual_temp REAL,
		set_temp REAL,
		heater_on INTEGER,
		recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
	)''')

UPGRADES = [
    db_upgrade0,
]

def upgrade_schema(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")

    current_version = query_single_value(conn, "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    start_version = current_version + 1 if current_version is not None else 0

    for upgrade_version in range(start_version, len(UPGRADES)):
        print("Applying upgrade %d" % upgrade_version)
        upgrade = UPGRADES[upgrade_version]
        upgrade(conn)
        conn.execute("INSERT INTO schema_version VALUES (?)", (upgrade_version,))

    conn.commit()

    print("There are %d entries in historical table" %
	query_single_value(conn, "SELECT count(*) FROM temp"))

def get_temp(bus):
	x = bus.read_i2c_block_data(THERMOMETER_ADDRESS, 0x05, 2)
	# Clear flags from the value
	x[0] = x[0] & 0x1f
	if x[0] & 0x10 == 0x10:
		x[0] = x[0] & 0x0f
		c = (x[0]*16 + x[1]/16.0) - 256
	else:
		c = x[0]*16 + x[1]/16.0
	f = c*9/5 + 32
	return f

# We're on /dev/i2c-1
bus = SMBus(1)

# Check manufacturer ID.
x = bus.read_i2c_block_data(THERMOMETER_ADDRESS, 0x06, 2)
if x[0] == 0 and x[1] == 0x54:
	# All good.
	# print("Manufacturer ID found at %x" % THERMOMETER_ADDRESS)
	pass
else:
	print("Manufacturer ID not found at %x" % THERMOMETER_ADDRESS)
	print(x)
	sys.exit(1)

# Check device ID.
x = bus.read_i2c_block_data(THERMOMETER_ADDRESS, 0x07, 1)
if x[0] == 0x04:
	# All good.
	# print("Device ID found at %d" % THERMOMETER_ADDRESS)
	pass
else:
	print("Device ID not found at %d" % THERMOMETER_ADDRESS)
	sys.exit(1)

# Read temperature.
f = get_temp(bus)
print("%.2f" % f)

# Turn on 7-segment display.
# bus.write_byte(SEVEN_SEGMENT_ADDRESS, HT16K33_OSCILLATOR_ON)
bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_OSCILLATOR_ON, [])
bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_DISPLAY_ON, [])

def draw_value(value, draw_colon):
	s = "%04d" % value
	buf = [0]*9
	for i in range(4):
		buf[POS[i]] = NUMBERS[ord(s[i]) - 0x30]
	buf[4] = 0x02 if draw_colon else 0x00
	bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, 0x00, buf)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ROT_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ROT_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

old_a = GPIO.input(ROT_A_PIN)
old_b = GPIO.input(ROT_B_PIN)

rot_value = 70*4
def cb(channel):
	global old_a, old_b, rot_value

	a = GPIO.input(ROT_A_PIN)
	b = GPIO.input(ROT_B_PIN)

	if a != old_a and b != old_b:
		# Can't tell.
		return

	if a == old_a and b == old_b:
		# No change.
		return

	d = 0
	if a != old_a:
		d = -1 if a ^ b else 1
	else:
		d = 1 if a ^ b else -1

	rot_value += d
	rot_value = max(rot_value, MIN_TEMP*4 - 2)
	rot_value = min(rot_value, MAX_TEMP*4 - 2)

	old_a = a
	old_b = b

GPIO.add_event_detect(ROT_A_PIN, GPIO.BOTH, callback=cb)
GPIO.add_event_detect(ROT_B_PIN, GPIO.BOTH, callback=cb)

conn = sqlite3.connect("data.db")
upgrade_schema(conn)

b = 15
bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_BRIGHTNESS | b, [])

db_write_time = time.time()

hist = []
while True:
	# Compute actual temperature.
	f = get_temp(bus)
	hist.append(f)
	while len(hist) > HIST_LEN:
		hist.pop(0)
	actual_temp = sum(hist) / len(hist)

	# Compute set temperature.
	set_temp = (rot_value + 2) // 4

	# Whether heater is on.
	heater_on = actual_temp < set_temp

	# Record settings to the database.
	now = time.time()
	if now - db_write_time > DB_WRITE_PERIOD:
		before = time.time()
		conn.execute('''INSERT INTO temp (actual_temp, set_temp, heater_on) VALUES (?, ?, ?)''',
			(actual_temp, set_temp, heater_on))
		conn.commit()
		db_write_time = now

	draw_value(int(actual_temp)*100 + set_temp, heater_on)
	time.sleep(0.1)

bus.close()

