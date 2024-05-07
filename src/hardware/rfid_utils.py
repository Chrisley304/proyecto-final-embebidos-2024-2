# import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()

try:
    while True:
        print("Place card on Reader")
        id, text = reader.read()
        print('ID: ', id)
        print("TEXT: ", text)
        # time.sleep(.5)
except:
    GPIO.cleanup()
    print("GPIO Good to Go")