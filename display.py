# Display-related code.

# Default address if you don't mess with address pins.
SEVEN_SEGMENT_ADDRESS = 0x70

HT16K33_DISPLAY_OFF = 0x80
HT16K33_DISPLAY_ON = 0x81
HT16K33_BRIGHTNESS = 0xE0
HT16K33_OSCILLATOR_ON = 0x21
POS = [0, 2, 6, 8]

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

def init(bus):
    # Turn on 7-segment display.
    bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_OSCILLATOR_ON, [])
    bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_DISPLAY_ON, [])

    # Full brightness.
    bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, HT16K33_BRIGHTNESS | 15, [])

# Draw the specified integer value on the display, with an optional colon.
def draw_value(bus, value, draw_colon):
    s = "%04d" % value
    buf = [0]*9
    for i in range(4):
        buf[POS[i]] = NUMBERS[ord(s[i]) - 0x30]
    buf[4] = 0x02 if draw_colon else 0x00
    bus.write_i2c_block_data(SEVEN_SEGMENT_ADDRESS, 0x00, buf)
