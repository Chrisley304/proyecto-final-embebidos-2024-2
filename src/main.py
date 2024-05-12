# import subprocess
import json
import schedule
import time
import threading
from utils import telegram_utils, notion_utils, lcd_utils
from hardware import fingerprint_utils, security_box_controller


# def something_happens():
#     """
#     Función de ejemplo para enviar un mensaje a todos los usuarios suscritos.
#     """
#     print("Enviando mensaje a los suscritos...")
#     message_text = "¡Hola! Se ha detectado un evento en la caja de seguridad."
#     telegram_utils.send_message_to_safe_users(message_text)
#     notion_utils.add_log_entry_to_notion()


def hardware_init():
    # TODO: Verificar que funcione bien lo del enrolamiento y buscar huella por el tema del id(numero)
    while True:
        if security_box_controller.isSystemActive():
            if fingerprint_utils.get_fingerprint():
                print("Detected #", fingerprint_utils.finger.finger_id, "with confidence", fingerprint_utils.finger.confidence)
                # something_happens()
            else:
                fingerprint_utils.enroll_finger()
        else:
            print("Access hardware unnactive. Waiting for user registration in Telegram...")

        time.sleep(2)


if __name__ == '__main__':
    try:
        print("Starting bot...")
        telegram_bot_thread = threading.Thread(target=telegram_utils.init)
        hardware_thread = threading.Thread(target=hardware_init)
        # lcd_utils.lcd_init()

        # Start the threads before joining them
        telegram_bot_thread.start()
        hardware_thread.start()

        # Esperar a que ambos hilos terminen
        telegram_bot_thread.join()
        hardware_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_utils.lcd_byte(0x01, lcd_utils.LCD_CMD)
