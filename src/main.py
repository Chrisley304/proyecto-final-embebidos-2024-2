# import subprocess
import json
import schedule
import time
import threading
from utils import telegram_utils, notion_utils


def something_happens():
    """
    Función de ejemplo para enviar un mensaje a todos los usuarios suscritos.
    """
    print("Enviando mensaje a los suscritos...")
    message_text = "¡Hola! Se ha detectado un evento en la caja de seguridad."
    telegram_utils.send_message_to_subscribers(message_text)
    notion_utils.add_log_entry_to_notion()


# def bot_polling_thread():
#     while True:
#         try:
#             telegram_bot.polling()
#         except Exception as e:
#             print(f"Error en el polling del bot: {e}")
#             time.sleep(5)

# Función para ejecutar el programador de tareas en un hilo separado


def testing():
    while True:
        something_happens()
        time.sleep(2)


if __name__ == '__main__':
    print("Starting bot...")
    telegram_bot_thread = threading.Thread(target=telegram_utils.init)
    test_thread = threading.Thread(target=testing)

    # Start the threads before joining them
    telegram_bot_thread.start()
    test_thread.start()

    # Esperar a que ambos hilos terminen
    telegram_bot_thread.join()
    test_thread.join()
