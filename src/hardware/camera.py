from picamera2 import Picamera2
import os
from PIL import Image 

class Camera():

    def __init__(self) -> None:
        self.picam = Picamera2()
        self.camera_config = self.picam.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
        self.picam.configure(self.camera_config)
        self.picam.start()

    def take_photo(self, date, type=""):
        """
            Función para tomar una foto con la camara y devolver el path a la misma.

            Params:
                date: Fecha de captura de la foto
                type: Tipo de foto que se puede capturar -> "ALERTA" | "RECONOCIMIENTO"
        """
        directory = "./other_photos/"

        if type == "ALERTA":
            directory = "./alert_photos/"
        elif type == "RECONOCIMIENTO":
            directory = "./photos_to_recog/"

        photo_path = os.path.join(directory, f"{date}.jpg")
        
        # Asegurar que el directorio exista
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.picam.capture_file(photo_path)

        # Se rota 180° la imagen debido a la posición de la camara
        img = Image.open(photo_path) 
        rotate_img= img.rotate(180)
        rotate_img.save(photo_path)

        return photo_path