# import subprocess
import json
import schedule
import time
import threading
from hardware import lcd
from utils import notion, telegram
from hardware.security_box_controller import RFID_sensor, Fingerprint_sensor, unlockSafe, playAlarm

def isSystemActive():
    return telegram.usersExists() and not telegram.isRecordingInput

isTakingInput = False
hardware_lock = threading.Lock()

# def something_happens():
#     """
#     Función de ejemplo para enviar un mensaje a todos los usuarios suscritos.
#     """
#     print("Enviando mensaje a los suscritos...")
#     message_text = "¡Hola! Se ha detectado un evento en la caja de seguridad."
#     telegram_utils.send_message_to_safe_users(message_text)
#     notion_utils.add_log_entry_to_notion()

def hardware_unlock_init(lock: threading.Lock):
     while True:
        if isSystemActive():
            with lock:
                isTakingInput = True
                if Fingerprint_sensor.get_fingerprint():
                    detected_id = Fingerprint_sensor.finger.finger_id
                    if Fingerprint_sensor.isFingerprintAuth(detected_id):
                        print("Detected #", Fingerprint_sensor.finger.finger_id, "with confidence", Fingerprint_sensor.finger.confidence)
                        unlockSafe()
                        time.sleep(1.5)
                    else:
                        print("Fingerprint not authorized")
                        playAlarm()
                        time.sleep(1.5)
                else:
                    RFID_sensor.unlock_rfid()
                
                isTakingInput = False

def test_init():
    while True:
        print("HOLA")
        time.sleep(1.5)

if __name__ == '__main__':
    try:
        print("Starting bot...")
        telegram_bot_thread = threading.Thread(target=telegram.init, args=[hardware_lock])
        fingerprint_thread = threading.Thread(target=hardware_unlock_init, args=[hardware_lock])
        # test_thread = threading.Thread(target=test_init)
        # lcd_utils.lcd_init()

        # Start the threads before joining them
        telegram_bot_thread.start()
        fingerprint_thread.start()
        # test_thread.start()

    except KeyboardInterrupt:
        pass
    # finally:
        # lcd_utils.lcd_byte(0x01, lcd_utils.LCD_CMD)
