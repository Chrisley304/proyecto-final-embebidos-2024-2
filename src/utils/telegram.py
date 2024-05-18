import os
from dotenv import load_dotenv
from telebot import telebot, types
import json
from hardware.security_box_controller import RFID_sensor, unlockSafe, Fingerprint_sensor
from main import isTakingInput
import threading
import adafruit_fingerprint
import time
from hardware.lcd import lcd_string, LCD_LINE_1, LCD_LINE_2
from utils.notion import get_last_n_events

# Carga de token de Telegram desde archivo .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
# Inicialización de cliente de Telegram utilizando el token API
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Carga de usuarios suscritos desde archivo JSON
try:
    with open('safe_users.json', 'r') as file:
        safe_users = json.load(file)
except FileNotFoundError:
    safe_users = {}

isRecordingInput = False

def start(message):
    """
    Función para manejar el comando de inicio del bot.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    if not usersExists():
        telegram_bot.reply_to(
            message, "¡Hola! Soy securitybot, yo te ayudare con la seguridad de tu caja fuerte.\nUsa /registro para registrarte como usuario autorizado y tener acceso a los controles de la caja fuerte.")
    else:
        telegram_bot.reply_to(
            message, "¡Hola! Soy securitybot, quien resguarda la caja fuerte de los Chambeadores!.\nDebes estar autorizado para acceder a los controles de la caja fuerte. Envía /solicitud para enviar una solicitud de autorización para continuar.")


def register_user(message:types.Message):
    """
    Función para manejar el proceso de registro.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    if not usersExists() or (user_id in safe_users and safe_users[user_id]['state'] == "awaiting_register"):
        sent_msg = telegram_bot.send_message(chat_id, "¡Bienvenido! Por favor envía tu nombre para completar el registro.", parse_mode="Markdown")
        # Cambiar el estado del usuario a 'awaiting_name'
        safe_users[user_id] = {'state': 'awaiting_name', 'chat_id': chat_id}
        
        # Escribir en el archivo JSON
        with open('safe_users.json', 'w') as file:
            json.dump(safe_users, file)

        telegram_bot.register_next_step_handler(sent_msg, handle_name_input)
    elif user_id in safe_users:
        telegram_bot.reply_to(
            message, "Ya estas registrado.")
    else:
        telegram_bot.reply_to(
            message, "No estas autorizado para registrarte. Solicita autorización enviando /solicitud.")

def handle_name_input(message):
    """
    Función para manejar el nombre enviado por el usuario.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    if user_id in safe_users and safe_users[user_id]['state'] == 'awaiting_name':
        # Guardar el nombre del usuario
        user_name = message.text
        
        # Pide al usuario una contraseña maestra para emergencias
        sent_msg = telegram_bot.send_message(chat_id, "Ahora por favor envía una contraseña maestra 🤫.")

        # Cambiar el estado del usuario a 'awaiting_password'
        safe_users[user_id]['name'] = user_name
        safe_users[user_id]['state'] = 'awaiting_password'

        telegram_bot.register_next_step_handler(sent_msg, handle_password_input)
        
        # Escribir en el archivo JSON
        with open('safe_users.json', 'w') as file:
            json.dump(safe_users, file)

    else:
        telegram_bot.send_message(
            user_id, "Error: No estás en el proceso de registro o ya has completado el registro.")

def handle_password_input(message):
    """
    Function to handle the master password submission.

    Params:
        message: Telegram message object.
    """
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    if user_id in safe_users and safe_users[user_id]['state'] == 'awaiting_password':
        # Save the user's master password
        master_password = message.text

        # Update the user's state to 'registered'
        safe_users[user_id]['password'] = master_password
        safe_users[user_id]['state'] = 'registered'

        # Write to the JSON file
        with open('safe_users.json', 'w') as file:
            json.dump(safe_users, file)

        telegram_bot.send_message(
            chat_id, "¡Registro exitoso! Ahora eres un usuario autorizado 🎉.")
    else:
        telegram_bot.send_message(
            chat_id, "Error: No estás en el proceso de registro o ya has completado el registro.")

def delete_safe_user(message):
    """
    Función para manejar la cancelación de la suscripción a las notificaciones.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)
    if user_id in safe_users:
        Fingerprint_sensor.delete_user_fingerprints(user_id)
        RFID_sensor.delete_user_rfid(user_id)

        del safe_users[user_id]
        with open('safe_users.json', 'w') as file:
            json.dump(safe_users, file)

        telegram_bot.reply_to(
            message, "Has borrado tu perfil del bot exitosamente. Hasta luego!")
    else:
        telegram_bot.reply_to(message, "No estás registrado actualmente.")
        print(f"UserID: {user_id}")
        print(safe_users)

def unlock_safe_with_master_password(message):
    """
    Función para desbloquear la caja fuerte con la contraseña maestra.

    Params:
        message_text: Texto del mensaje a enviar.
    """
    user_id = str(message.from_user.id)

    if user_id in safe_users:
        sent_msg = telegram_bot.send_message(user_id, "Envía tu contraseña maestra para desbloquear la caja fuerte (recuerda borrar el mensaje después de eso).")
        telegram_bot.register_next_step_handler(sent_msg, handle_unlock_with_password_input)
    else:
        telegram_bot.reply_to(message, "No tienes permiso para hacer eso.")

def handle_unlock_with_password_input(message:types.Message):
    """
    Función para recibir la contraseña maestra y desbloquear la caja fuerte.

    Params:
        message_text: Texto del mensaje a enviar.
    """
    user_id = str(message.from_user.id)

    if user_id in safe_users:
        password_input = message.text

        if password_input == safe_users[user_id]["password"]:
            user_name = safe_users[user_id]["name"] if safe_users[user_id]["name"] else "Desconocido"
            unlockSafe(user_name,"Contraseña maestra")
            telegram_bot.send_message(user_id, "Desbloqueando caja fuerte ahora...")
        else:
            telegram_bot.send_message(user_id, "Contraseña incorrecta.")
    else:
        telegram_bot.reply_to(message, "No tienes permiso para hacer eso.")

def send_message_to_safe_users(message_text):
    """
    Función para enviar un mensaje a todos los usuarios suscritos.

    Params:
        message_text: Texto del mensaje a enviar.
    """
    for user_id in safe_users.keys():
        telegram_bot.send_message(safe_users[user_id]["chat_id"], message_text)

def save_facial_recog_photo(message):
    """
    Función para registrar una foto de reconocimiento facial del usuario.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    telegram_bot.reply_to(
            message, "Proximamente!")

def record_rfid_card(message:types.Message):
    """
    Función para registrar una foto de reconocimiento facial del usuario.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)

    if isUserAutorized(user_id):
        isRecordingInput = True
        telegram_bot.reply_to(message, "Acerca el tag RFID al sensor")
        lcd_string("Acerca el tag", LCD_LINE_1)
        lcd_string("para registrarlo", LCD_LINE_2)
        rfid_id = RFID_sensor.read_rfid_id()
        if RFID_sensor.record_rfid_tag(rfid_id, safe_users[user_id]["name"], user_id):
            telegram_bot.send_message(user_id, "El Tag fue registrado exitosamente")
        else:
            telegram_bot.send_message(user_id, "El Tag ya esta registrado")

    isRecordingInput = False

def record_fingerprint(message:types.Message):
    """
    Función para registrar una huella dactilar del usuario.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)

    if isUserAutorized(user_id):
        istelegramRecordingInput = True
        while isTakingInput:
            pass
        user_name = safe_users[user_id]['name']

        if enroll_fingerprint_with_telegram_feedback(user_name, user_id):
            telegram_bot.send_message(user_id, "Huella registrada exitosamente")
        else:
            telegram_bot.send_message(user_id, "Error al registrar la huella")
    else:
        telegram_bot.reply_to(message, "No tienes permiso para hacer eso.")

    istelegramRecordingInput = False

def view_last_safe_box_activity(message: types.Message):
    """
        Función para obtener los ultimos 3 eventos registrados en la caja de seguridad.

        Params:
            message: Objeto de mensaje de Telegram.
    """
    user_id = str(message.from_user.id)

    if isUserAutorized(user_id):
        events_messages = get_last_n_events(3)

        for event in events_messages:
            sendMesagetoUser(event, user_id)

def sendMesagetoUser(message:str, user_id:str):
    """
    Función para enviar un mensaje a un usuario en especifico.

    Params:
        message: Cadena de texto a enviar.
        user_id: ID del usuario al que se va a enviar el mensaje.
    """
    telegram_bot.send_message(user_id, message, parse_mode="Markdown")

def send_help(message):
    """
        Función para enviar los comandos disponibles al usuario.

        Params:
            message: Objeto de mensaje de Telegram.    
    """
    user_id = str(message.from_user.id)

    help_text = """
Aquí tienes una lista de los comandos disponibles y sus descripciones:
/start: Inicia el bot y recibe un mensaje de bienvenida.
/veractividad: Revisa la última actividad de la caja fuerte, incluyendo accesos y eventos recientes.
/reconocimientofacial: Desbloquea la caja fuerte enviando una foto de tu cara para el reconocimiento facial.
/desbloqueomaestro: Si tienes problemas con los sensores de la caja fuerte, utiliza tu contraseña maestra para abrirla.
/nuevorfid: Una vez registrado, añade un nuevo tag RFID para acceder a la caja fuerte.
/nuevahuella: Una vez registrado, añade una nueva huella digital a la caja fuerte.
/nuevoreconocimientofacial: Una vez registrado, envía una foto para añadirla al sistema de reconocimiento facial de la caja fuerte.
/registro: Si eres un usuario autorizado o el primer usuario, regístrate en el bot enviando tu nombre.
/solicitud: Envía una solicitud a los "super usuarios" para obtener permisos de interacción con la caja fuerte.
/revisarsolicitudes: Los super usuarios pueden revisar las solicitudes de personas que desean ser autorizadas.
/borrarperfil: Elimina tu perfil del bot y revoca tus permisos.
/ayuda: Muestra este mensaje de ayuda con la lista de comandos y sus descripciones.
    """

    telegram_bot.send_message(user_id, help_text, parse_mode="Markdown")


def init(lock: threading.Lock):
    """
        Función para iniciar el bot de Telegram.

        Params:
            lock: Objeto Lock de threading para evitar choques con variables concurrentes.
    """

    # Comandos del bot
    @telegram_bot.message_handler(commands=['start'])
    def handle_start(message):
        start(message)

    @telegram_bot.message_handler(commands=['registro'])
    def handle_register(message):
        register_user(message)

    @telegram_bot.message_handler(commands=['nuevoreconocimientofacial'])
    def handle_new_photo_rec(message):
        save_facial_recog_photo(message)

    @telegram_bot.message_handler(commands=['borrarperfil'])
    def handle_delete_profile(message):
        delete_safe_user(message)

    @telegram_bot.message_handler(commands=['desbloqueomaestro'])
    def handle_unlock_safe(message):
        unlock_safe_with_master_password(message)

    @telegram_bot.message_handler(commands=['nuevorfid'])
    def handle_record_new_rfid(message):
        with lock:
            record_rfid_card(message)

    @telegram_bot.message_handler(commands=['nuevahuella'])
    def handle_new_fingerprint(message):
        with lock:
            record_fingerprint(message)

    @telegram_bot.message_handler(commands=['veractividad'])
    def handle_view_last_activity(message):
        view_last_safe_box_activity(message)
    
    @telegram_bot.message_handler(commands=['ayuda'])
    def handle_help(message):
        send_help(message)

    while True:
        telegram_bot.polling()

def usersExists():
    """
    Función para saber si existen usuarios registrados en el bot.

    Returns: Bool
    """
    return len(safe_users.keys()) > 0

def isUserAutorized(user_id):
    """
    Función para saber si el usuario esta registrado correctamente.

    Returns: Bool
    """
    return user_id in safe_users and safe_users[user_id]['state'] == 'registered'

def enroll_fingerprint_with_telegram_feedback(username:str, user_id:str):
    """
    Take a 2 finger images and template it, then store in 'location'
    
    Params:
        username: Name of the user that is registering the fingerprint.
        user_id: Telegram ID of the user to send feedback.
    """
    location = len(Fingerprint_sensor.auth_fingerprints)

    if location < 0 or location > Fingerprint_sensor.finger.library_size - 1:
        return False

    for fingerimg in range(1, 3):
        if fingerimg == 1:
            lcd_string("Coloca el dedo", LCD_LINE_1)
            lcd_string("en el sensor", LCD_LINE_2)
            sendMesagetoUser("Coloca el dedo en el sensor...", user_id)
        else:
            lcd_string("Coloca el dedo", LCD_LINE_1)
            lcd_string("en el sensor", LCD_LINE_2)
            sendMesagetoUser("Coloca el mismo dedo en el sensor de nuevo...", user_id)

        while True:
            i = Fingerprint_sensor.finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                sendMesagetoUser("Error al guardar huella digital: Intentelo de nuevo", user_id)
                print("Imaging error")
                return False
            else:
                sendMesagetoUser("Error al guardar huella digital: Intentelo de nuevo", user_id)
                print("Other error")
                return False

        print("Templating...", end="")
        i = Fingerprint_sensor.finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                sendMesagetoUser("Error al guardar huella digital: La imagen esta borrosa", user_id)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                sendMesagetoUser("Error al guardar huella digital: No se identifico huella digital", user_id)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                sendMesagetoUser("Error al guardar huella digital: Imagen invalida", user_id)
            else:
                sendMesagetoUser("Error al guardar huella digital: Intentelo de nuevo", user_id)
            return False

        if fingerimg == 1:
            lcd_string("Quita el dedo", LCD_LINE_1)
            lcd_string("del sensor", LCD_LINE_2)
            sendMesagetoUser("Retira el dedo del sensor", user_id)
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                lcd_string("Coloca el dedo", LCD_LINE_1)
                lcd_string("en el sensor", LCD_LINE_2)
                sendMesagetoUser("Vuelve a colocar el dedo en el sensor", user_id)
                i = Fingerprint_sensor.finger.get_image()

    print("Creating model...", end="")
    i = Fingerprint_sensor.finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            sendMesagetoUser("Error al guardar huella digital: Huellas no coinciden", user_id)
            print("Prints did not match")
        else:
            sendMesagetoUser("Error al guardar huella digital: Intentelo de nuevo", user_id)
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = Fingerprint_sensor.finger.store_model(location)
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

    Fingerprint_sensor.auth_fingerprints.append({"location": location, "user_name": username, "user_id": user_id})

    with open('auth_fingerprints.json', 'w') as file:
            json.dump(Fingerprint_sensor.auth_fingerprints, file)

    return True