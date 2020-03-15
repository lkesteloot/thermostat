# Relay-related code.

import time

# sudo apt-get install python3-rpi.gpio
import RPi.GPIO as GPIO

# Assumes GPIO.BOARD.
SET_PIN = 13
UNSET_PIN = 11

def init():
    GPIO.setup(SET_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(UNSET_PIN, GPIO.OUT, initial=GPIO.LOW)

def set_relay(on):
    pin = SET_PIN if on else UNSET_PIN
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.010) # 10ms
    GPIO.output(pin, GPIO.LOW)

