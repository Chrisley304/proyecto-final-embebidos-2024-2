from picamera2 import Picamera2

class Camera():

    def __init__(self) -> None:
        self.picam = Picamera2()
        self.camera_config = self.picam.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
        self.picam.configure(self.camera_config)
        self.picam.start()

    def take_photo(self, date):
        """
            Función para tomar una foto con la camara y devolver el path a la misma.

            Params:
                date: Fecha de captura de la foto
        """
        photo_path = f"./alert_photos/{date}.jpg"

        self.picam.capture_file(photo_path)

        return photo_path