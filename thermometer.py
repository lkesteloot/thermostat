# Therometer-related code.

import sys

# Default address if you don't mess with address pins.
THERMOMETER_ADDRESS = 0x18

def init(bus):
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

# Get the temperature in Fahrenheit.
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
