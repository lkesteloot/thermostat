import sys

# sudo apt-get install python3-smbus
from smbus import SMBus

# Default address if you don't mess with address pins.
ADDRESS = 0x18

# We're on /dev/i2c-1
bus = SMBus(1)

# Check manufacturer ID.
x = bus.read_i2c_block_data(ADDRESS, 0x06, 2)
if x[0] == 0 and x[1] == 0x54:
	# All good.
	# print("Manufacturer ID found at %x" % ADDRESS)
	pass
else:
	print("Manufacturer ID not found at %x" % ADDRESS)
	print(x)
	sys.exit(1)

# Check device ID.
x = bus.read_i2c_block_data(ADDRESS, 0x07, 1)
if x[0] == 0x04:
	# All good.
	# print("Device ID found at %d" % ADDRESS)
	pass
else:
	print("Device ID not found at %d" % ADDRESS)
	sys.exit(1)

# Read temperature.
x = bus.read_i2c_block_data(ADDRESS, 0x05, 2)
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
print("%.2f" % f)

bus.close()

