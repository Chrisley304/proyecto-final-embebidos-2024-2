# import subprocess
import json
import schedule
import time
import threading
from utils import telegram_utils, notion_utils
from hardware import fingerprint_utils, security_box_controller


def something_happens():
    """
    Función de ejemplo para enviar un mensaje a todos los usuarios suscritos.
    """
    print("Enviando mensaje a los suscritos...")
    message_text = "¡Hola! Se ha detectado un evento en la caja de seguridad."
    telegram_utils.send_message_to_safe_users(message_text)
    notion_utils.add_log_entry_to_notion()


# def bot_polling_thread():
#     while True:
#         try:
#             telegram_bot.polling()
#         except Exception as e:
#             print(f"Error en el polling del bot: {e}")
#             time.sleep(5)

# Función para ejecutar el programador de tareas en un hilo separado


def access_hardware():
    while True:
        if security_box_controller.isSystemActive:
            if fingerprint_utils.get_fingerprint():
                print("Detected #", fingerprint_utils.finger.finger_id, "with confidence", fingerprint_utils.finger.confidence)
                something_happens()
            else:
                fingerprint_utils.enroll_finger()
        else:
            print("Access hardware unnactive. Waiting for user registration in Telegram...")

        time.sleep(2)


if __name__ == '__main__':
    print("Starting bot...")
    telegram_bot_thread = threading.Thread(target=telegram_utils.init)
    test_thread = threading.Thread(target=access_hardware)

    # Start the threads before joining them
    telegram_bot_thread.start()
    test_thread.start()

    # Esperar a que ambos hilos terminen
    telegram_bot_thread.join()
    test_thread.join()
