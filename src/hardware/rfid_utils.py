# import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import json

reader = SimpleMFRC522()

# Carga de usuarios suscritos desde archivo JSON
try:
    with open('authorized_rfid.json', 'r') as file:
        authorized_rfid = json.load(file)
except FileNotFoundError:
    authorized_rfid = {}

def record_rfid_tag(rfid_id, user_name):
    """
    Función para guardar un tag RFID como llave para abrir la caja fuerte.

    Params:
        rfid_id: ID del tag RFID
        user_name: Nombre del usuario del tag
    """

    if rfid_id not in authorized_rfid:

        authorized_rfid[rfid_id] = {"user_name": user_name}
        # Escribir en el archivo JSON
        with open('authorized_rfid.json', 'w') as file:
            json.dump(authorized_rfid, file)

        return True
    else:
        return False

def read_rfid_id():
    """
    Función para leer el id de un tag RFID.

    Returns: id -> str
    """
    try:
        print("Place card on Reader")
        id, text = reader.read()
        return str(id)
    except:
        GPIO.cleanup()