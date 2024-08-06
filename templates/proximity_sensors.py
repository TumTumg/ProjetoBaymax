import RPi.GPIO as GPIO

class ProximitySensors:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def is_visitor_near(self):
        return GPIO.input(self.pin) == GPIO.HIGH
