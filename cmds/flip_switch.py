import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

# Define pin where switch is connected
SWITCH_PIN = 17

# Set up the pin with pull-up resistor
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define a callback function to run when switch flips
def switch_callback(channel):
    if GPIO.input(channel) == GPIO.LOW:  # Flipped (pulled to GND)
        my_method(0)
        return
    my_method(1)

# Set up event detection
GPIO.add_event_detect(SWITCH_PIN, GPIO.FALLING, callback=switch_callback, bouncetime=300)

try:
    print("Listening for switch flip. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
