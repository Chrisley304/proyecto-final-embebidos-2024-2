from hardware.rfid import RFID
from hardware.fingerprint import Fingerprint
import vlc
from pygame import mixer

RFID_sensor = RFID()
Fingerprint_sensor = Fingerprint()
alarmON = False

mixer.init()
mixer.music.load("src/assets/alarm.mp3")

def unlockSafe():
    global alarmON
    print("MOCK: Unlocking safe")
    pauseAlarm()
    alarmON = False

    return False

def playAlarm():
    global alarmON

    print("ALARM ACTIVED")

    if not alarmON:
        alarmON = True
        mixer.music.play(-1,0)

def pauseAlarm():
    mixer.music.pause()