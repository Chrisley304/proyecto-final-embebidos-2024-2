# import subprocess
import json
import schedule
import time
import threading
from utils import telegram_utils, notion_utils, lcd_utils
from hardware import fingerprint_utils, security_box_controller, rfid_utils

def isSystemActive():
    return telegram_utils.usersExists() and not telegram_utils.isRecordingInput

# def something_happens():
#     """
#     Función de ejemplo para enviar un mensaje a todos los usuarios suscritos.
#     """
#     print("Enviando mensaje a los suscritos...")
#     message_text = "¡Hola! Se ha detectado un evento en la caja de seguridad."
#     telegram_utils.send_message_to_safe_users(message_text)
#     notion_utils.add_log_entry_to_notion()

def fingerprint_scanner_init():
     while True:
        if isSystemActive():
            if fingerprint_utils.get_fingerprint():
                detected_id = fingerprint_utils.finger.finger_id
                if detected_id < len(fingerprint_utils.auth_fingerprints):
                    print("Detected #", fingerprint_utils.finger.finger_id, "with confidence", fingerprint_utils.finger.confidence)
                else:
                    print("Fingerprint not authorized")

        time.sleep(2)

def rfid_scanner_init():
    while True:
        if isSystemActive():
            if rfid_utils.unlock_rfid():
                print("CAJA DESBLOQUEADA")
            else:
                if isSystemActive():
                    print("ACCESO DENEGADO")

        time.sleep(2)


if __name__ == '__main__':
    try:
        print("Starting bot...")
        telegram_bot_thread = threading.Thread(target=telegram_utils.init)
        fingerprint_thread = threading.Thread(target=fingerprint_scanner_init)
        rfid_thread = threading.Thread(target=rfid_scanner_init)
        # lcd_utils.lcd_init()

        # Start the threads before joining them
        telegram_bot_thread.start()
        fingerprint_thread.start()
        rfid_thread.start()

        # Esperar a que ambos hilos terminen
        telegram_bot_thread.join()
        fingerprint_thread.join()
        rfid_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_utils.lcd_byte(0x01, lcd_utils.LCD_CMD)
