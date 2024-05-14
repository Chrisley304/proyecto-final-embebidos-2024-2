import os
from dotenv import load_dotenv
from telebot import telebot, types
import json
from hardware.security_box_controller import RFID_sensor, unlockSafe, Fingerprint_sensor
from main import isTakingInput
import threading

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
            unlockSafe()
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
        rfid_id = RFID_sensor.read_rfid_id()
        if RFID_sensor.record_rfid_tag(rfid_id, safe_users[user_id]["name"]):
            telegram_bot.send_message(user_id,"El Tag fue registrado exitosamente")
        else:
            telegram_bot.send_message(user_id,"El Tag ya esta registrado")

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
        telegram_bot.reply_to(message, "Coloca tu huella en el sensor...")
        if Fingerprint_sensor.enroll_finger(user_name):
            telegram_bot.send_message(user_id, "Huella registrada exitosamente")
        else:
            telegram_bot.send_message(user_id, "Error al registrar la huella")
    else:
        telegram_bot.reply_to(message, "No tienes permiso para hacer eso.")

    istelegramRecordingInput = False

def init(lock: threading.Lock):
    """
    Función para iniciar el bot de Telegram.
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

    @telegram_bot.message_handler(commands=['desbloquear'])
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