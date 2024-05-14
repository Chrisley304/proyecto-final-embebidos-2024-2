from hardware.rfid import RFID
from hardware.fingerprint import Fingerprint

RFID_sensor = RFID()
Fingerprint_sensor = Fingerprint()

def unlockSafe():
    print("MOCK: Unlocking safe")
    return False