from hardware.rfid import RFID
from hardware.fingerprint import Fingerprint
import vlc
from pygame import mixer
from utils.notion import add_log_entry_to_notion
from datetime import datetime

RFID_sensor = RFID()
Fingerprint_sensor = Fingerprint()
alarmON = False

mixer.init()
mixer.music.load("src/assets/alarm.mp3")

def unlockSafe(user_name, unlock_type):
    """
        Funcion para abrir la caja fuerte una vez que se autentifico al usuario.

        Params:
            user_name: Nombre del usuario.
            unlock_type: Medio por el cual se desbloqueo la caja fuerte.
    """
    global alarmON
    print("MOCK: Unlocking safe")
    pauseAlarm()
    alarmON = False
    add_log_entry_to_notion(user_name, "Apertura", datetime.now(), unlock_type)

    return False

def playAlarm(unlock_type):
    """
        Función para activar la alarma de la caja fuerte cuando un desconocido intenta ingresar a ella.

        Params:
            unlock_type: Medio por el cual se intento desbloquear la caja fuerte.
    """
    global alarmON

    print("ALARM ACTIVED")

    if not alarmON:
        alarmON = True
        mixer.music.play(-1,0)

    add_log_entry_to_notion("Intruso", "Intento apertura", datetime.now(), unlock_type)

def pauseAlarm():
    mixer.music.pause()