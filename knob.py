# Knob-related code.

# sudo apt-get install python3-rpi.gpio
import RPi.GPIO as GPIO

# Assumes GPIO.BOARD.
ROT_A_PIN = 16
ROT_B_PIN = 18

MIN_TEMP = 60
MAX_TEMP = 90

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

def init():
    global old_a, old_b

    GPIO.setup(ROT_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ROT_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(ROT_A_PIN, GPIO.BOTH, callback=cb)
    GPIO.add_event_detect(ROT_B_PIN, GPIO.BOTH, callback=cb)

    old_a = GPIO.input(ROT_A_PIN)
    old_b = GPIO.input(ROT_B_PIN)

def get_temp():
    global rot_value
    return (rot_value + 2) // 4

def set_temp(temp):
    global rot_value
    rot_value = temp*4 - 2

