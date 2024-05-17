# import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import json
from hardware import security_box_controller

class RFID:

    def __init__(self):
        self.reader = SimpleMFRC522()
        self.authorized_rfid = self._init_authorized_rfid_from_json()

    def _init_authorized_rfid_from_json(self):
        """
            Carga de usuarios suscritos desde archivo JSON
        """
        try:
            with open('authorized_rfid.json', 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            return {}

    def record_rfid_tag(self,rfid_id, user_name, user_id):
        """
        Función para guardar un tag RFID como llave para abrir la caja fuerte.

        Params:
            rfid_id: ID del tag RFID
            user_name: Nombre del usuario del tag
            user_id: ID del usuario
        """

        if rfid_id not in self.authorized_rfid:

            self.authorized_rfid[rfid_id] = {"user_name": user_name, "user_id": user_id}
            # Escribir en el archivo JSON
            with open('authorized_rfid.json', 'w') as file:
                json.dump(self.authorized_rfid, file)

            return True
        else:
            return False

    def read_rfid_id(self):
        """
        Función para leer el id de un tag RFID.

        Returns: id -> str
        """
        try:
            print("Waiting for RFID card...")
            id, text = self.reader.read()
            return str(id)
        except:
            GPIO.cleanup()

    def get_rfid_entry(self):
        """
        Función para leer el id de un tag RFID.

        Returns: id -> str
        """
        try:
            id, text = self.reader.read_no_block()
            return str(id) if id else None
        except:
            GPIO.cleanup()

    def unlock_rfid(self):
        """
        Función para leer tags RFID para desbloquear la caja si el ID del RFID esta autorizado.

        Returns: Bool
        """

        id = self.get_rfid_entry()
        if id != None:
            if id in self.authorized_rfid:
                print("CAJA DESBLOQUEADA")
                user_name = self.get_rfid_user_name(id)
                security_box_controller.unlockSafe(user_name, "RFID")
                return True
            else:
                print("ACCESO DENEGADO")
                security_box_controller.playAlarm("RFID")
                return False
    
    def get_rfid_user_name(self, rfid_id):
        """
            Funcion para obtener el nombre del usuario detectado mediante su huella.

            Params:
                rfid_id: ID de la huella detectada.
        """
        return self.authorized_rfid[rfid_id]["user_name"] if self.authorized_rfid[rfid_id]["user_name"] else "Desconocido"
    
    def delete_user_rfid(self, user_id):
        """
            Función para eliminar los tags rfid almacenados de un usuario.

            Params:
                user_id: ID del usuario.
        """
        filtered_auth_rfid = {key: value for key, value in self.authorized_rfid.items() if value["user_id"] != user_id}
        with open('authorized_rfid.json', 'w') as file:
            json.dump(filtered_auth_rfid, file)