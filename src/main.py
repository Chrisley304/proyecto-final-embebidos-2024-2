import time
import threading
from hardware.lcd import lcd_init, LCD_CMD, lcd_byte, lcd_string, LCD_LINE_1, LCD_LINE_2
from utils import telegram
from hardware.security_box_controller import RFID_sensor, Fingerprint_sensor, unlockSafe, playAlarm
import RPi.GPIO as GPIO

def isSystemActive():
    return telegram.users_exists() and not telegram.isRecordingInput

isTakingInput = False
hardware_lock = threading.Lock()

def hardware_unlock_init(lock: threading.Lock):
    lcd_init()

    while True:
        if isSystemActive():
            lcd_string("Usa tu huella o",LCD_LINE_1)
            lcd_string("RFID para abrir",LCD_LINE_2)
            with lock:
                isTakingInput = True
                if Fingerprint_sensor.get_fingerprint():
                    detected_id = Fingerprint_sensor.finger.finger_id
                    if Fingerprint_sensor.isFingerprintAuth(detected_id):
                        user_name = Fingerprint_sensor.get_fingerprint_user_name(detected_id)
                        print(f"Detected #{Fingerprint_sensor.finger.finger_id} with {Fingerprint_sensor.finger.confidence} confidence. Username: {user_name}")
                        unlockSafe(user_name, "Huella dactilar")
                        # time.sleep(2.5)
                    else:
                        print("Fingerprint not authorized")
                        playAlarm("Huella dactilar")
                else:
                    RFID_sensor.unlock_rfid()
                
                isTakingInput = False

if __name__ == '__main__':
    try:
        telegram_bot_thread = threading.Thread(target=telegram.init, args=[hardware_lock])
        hardware_unlock_thread = threading.Thread(target=hardware_unlock_init, args=[hardware_lock])
        # lcd_utils.lcd_init()

        # Start the threads before joining them
        telegram_bot_thread.start()
        hardware_unlock_thread.start()

        print("Safe is active")

    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        GPIO.cleanup()