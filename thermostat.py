import sys
import time

# sudo apt-get install python3-smbus
from smbus import SMBus

HT16K33_DISPLAY_OFF = 0x80
HT16K33_DISPLAY_ON = 0x81
HT16K33_CMD_BRIGHTNESS = 0xE0
HT16K33_OSCILLATOR_ON = 0x21

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
    0x77, # a
    0x7C, # b
    0x39, # C
    0x5E, # d
    0x79, # E
    0x71, # F
    0x40, # -
]

def get_temp(bus):
	x = bus.read_i2c_block_data(THERMOMETER_ADDRESS, 0x05, 2)
	# Clear flags from the value
	x[0] = x[0] & 0x1f
	if x[0] & 0x10 == 0x10:
		x[0] = x[0] & 0x0f
		c = (x[0]*16 + x[1]/16.0) - 256
	else:
		c = x[0]*16 + x[1]/16.0
	# print("Temperature: %.2f C" % c)
	f = c*9/5 + 32
	# print("Temperature: %.2f F" % f)
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

POS = [0, 2, 6, 8]
while True:
	buf = [0]*9
	value = int(get_temp(bus)*100)
	s = "%04d" % value
	for i in range(4):
		buf[POS[i]] = NUMBERS[ord(s[i]) - 0x30]
	buf[POS[1]] |= 0x80

	bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, 0x00, buf)
	time.sleep(0.1)

bus.close()

