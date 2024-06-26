import time
import serial
import adafruit_fingerprint
import json
from hardware import security_box_controller

class Fingerprint:

    def __init__(self):
        self.uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
        self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)
        self.auth_fingerprints = self._init_authorized_rfid_from_json()

    def _init_authorized_rfid_from_json(self):
        """
            Carga de usuarios suscritos desde archivo JSON
        """
        try:
            with open('auth_fingerprints.json', 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            return []

    def get_fingerprint(self):
        """Get a finger print image, template it, and see if it matches!"""
        # print("Waiting for image...")
        if self.finger.get_image() != adafruit_fingerprint.OK:
            return False
        print("Reading fingerprint...")
        if self.finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        print("Searching fingerprint...")
        if self.finger.finger_search() != adafruit_fingerprint.OK:
            print("Fingerprint not found")
            security_box_controller.playAlarm("Huella dactilar")
            return False
        return True

    def get_fingerprint_detail(self):
        """Get a finger print image, template it, and see if it matches!
        This time, print out each error instead of just returning on failure"""
        print("Getting image...", end="")
        i = self.finger.get_image()
        if i == adafruit_fingerprint.OK:
            print("Image taken")
        else:
            if i == adafruit_fingerprint.NOFINGER:
                print("No finger detected")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
            else:
                print("Other error")
            return False

        print("Templating...", end="")
        i = self.finger.image_2_tz(1)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        print("Searching...", end="")
        i = self.finger.finger_fast_search()
        # pylint: disable=no-else-return
        # This block needs to be refactored when it can be tested.
        if i == adafruit_fingerprint.OK:
            print("Found fingerprint!")
            return True
        else:
            if i == adafruit_fingerprint.NOTFOUND:
                print("No match found")
            else:
                print("Other error")
            return False

    def delete_user_fingerprints(self, user_id):
        """
            Función para eliminar las huellas almacenadas de un usuario.

            Params:
                user_id: ID del usuario.
        """
        filtered_auth_fingers = [finger for finger in self.auth_fingerprints if finger['user_id'] != user_id]
        print(filtered_auth_fingers)
        with open('auth_fingerprints.json', 'w') as file:
            json.dump(filtered_auth_fingers, file)

    # pylint: disable=too-many-statements
    def enroll_finger(self, username:str, user_id:str):
        """
        Take a 2 finger images and template it, then store in 'location'
        
        Params:
            username: Nombre del usuario
            user_id: ID del usuario
        """
        location = len(self.auth_fingerprints)

        if location < 0 or location > self.finger.library_size - 1:
            return False

        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place self.finger on sensor...", end="")
            else:
                print("Place same finger again...", end="")

            while True:
                i = self.finger.get_image()
                if i == adafruit_fingerprint.OK:
                    print("Image taken")
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print(".", end="")
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Imaging error")
                    return False
                else:
                    print("Other error")
                    return False

            print("Templating...", end="")
            i = self.finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Templated")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Image too messy")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Could not identify features")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False

            if fingerimg == 1:
                print("Remove finger")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = self.finger.get_image()

        print("Creating model...", end="")
        i = self.finger.create_model()
        if i == adafruit_fingerprint.OK:
            print("Created")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                print("Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing model #%d..." % location, end="")
        i = self.finger.store_model(location)
        if i == adafruit_fingerprint.OK:
            print("Stored")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Bad storage location")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False

        self.auth_fingerprints.append({"location": location, "user_name": username, "user_id": user_id})

        with open('auth_fingerprints.json', 'w') as file:
                json.dump(self.auth_fingerprints, file)

        return True


    def save_fingerprint_image(self,filename):
        """Scan fingerprint then save image to filename."""
        while self.finger.get_image():
            pass

        # let PIL take care of the image headers and file structure
        from PIL import Image  # pylint: disable=import-outside-toplevel

        img = Image.new("L", (256, 288), "white")
        pixeldata = img.load()
        mask = 0b00001111
        result = self.finger.get_fpdata(sensorbuffer="image")

        # this block "unpacks" the data received from the fingerprint
        #   module then copies the image data to the image placeholder "img"
        #   pixel by pixel.  please refer to section 4.2.1 of the manual for
        #   more details.  thanks to Bastian Raschke and Danylo Esterman.
        # pylint: disable=invalid-name
        x = 0
        # pylint: disable=invalid-name
        y = 0
        # pylint: disable=consider-using-enumerate
        for i in range(len(result)):
            pixeldata[x, y] = (int(result[i]) >> 4) * 17
            x += 1
            pixeldata[x, y] = (int(result[i]) & mask) * 17
            if x == 255:
                x = 0
                y += 1
            else:
                x += 1

        if not img.save(filename):
            return True
        return False

    def isFingerprintAuth(self, detected_id):
        """
            Función que devuelve si el id detectado esta autorizado para abrir la caja o no.

            Params:
                detected_id: ID de la huella detectada.
        """
        return detected_id < len(self.auth_fingerprints)
    
    def get_fingerprint_user_name(self, detected_id):
        """
            Funcion para obtener el nombre del usuario detectado mediante su huella.

            Params:
                detected_id: ID de la huella detectada.
        """

        return self.auth_fingerprints[detected_id]["user_name"]

    ##################################################


    def get_num(max_number):
        """Use input() to get a valid number from 0 to the maximum size
        of the library. Retry till success!"""
        i = -1
        while (i > max_number - 1) or (i < 0):
            try:
                i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
            except ValueError:
                pass
        return i

"""
while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates: ", finger.templates)
    if finger.count_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Number of templates found: ", finger.template_count)
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to get system parameters")
    print("Size of template library: ", finger.library_size)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("s) save fingerprint image")
    print("r) reset library")
    print("q) quit")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num(finger.library_size))
    if c == "f":
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger not found")
    if c == "d":
        if finger.delete_model(get_num(finger.library_size)) == adafruit_fingerprint.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
    if c == "s":
        if save_fingerprint_image("fingerprint.png"):
            print("Fingerprint image saved")
        else:
            print("Failed to save fingerprint image")
    if c == "r":
        if finger.empty_library() == adafruit_fingerprint.OK:
            print("Library empty!")
        else:
            print("Failed to empty library")
    if c == "q":
        print("Exiting fingerprint example program")
        raise SystemExit
"""