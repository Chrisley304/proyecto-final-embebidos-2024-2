import os
from dotenv import load_dotenv
from telebot import telebot, types
import json

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


def register_user(message):
    """
    Función para manejar el proceso de registro.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = message.chat.id
    if not usersExists() or (user_id in safe_users and safe_users[user_id]['state'] == "awaiting_register"):
        sent_msg = telegram_bot.send_message(message.chat.id, "¡Bienvenido! Por favor envía tu nombre para completar el registro.", parse_mode="Markdown")
        # Cambiar el estado del usuario a 'awaiting_name'
        safe_users[user_id] = {'state': 'awaiting_name'}
        
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
    user_id = message.chat.id
    if user_id in safe_users and safe_users[user_id]['state'] == 'awaiting_name':
        # Guardar el nombre del usuario
        user_name = message.text
        
        # Pide al usuario una contraseña maestra para emergencias
        sent_msg = telegram_bot.send_message(user_id, "Ahora por favor envía una contraseña maestra 🤫.")

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
    user_id = message.chat.id
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
            user_id, "¡Registro exitoso! Ahora eres un usuario autorizado 🎉.")
    else:
        telegram_bot.send_message(
            user_id, "Error: No estás en el proceso de registro o ya has completado el registro.")



def delete_safe_user(message):
    """
    Función para manejar la cancelación de la suscripción a las notificaciones.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = message.chat.id
    if user_id in safe_users:
        safe_users.remove(user_id)
        with open('safe_users.json', 'w') as file:
            json.dump(safe_users, file)
        telegram_bot.reply_to(
            message, "Has borrado tu perfil del bot exitosamente. Hasta luego!")
    else:
        telegram_bot.reply_to(message, "No estás suscrito actualmente.")

def send_message_to_safe_users(message_text):
    """
    Función para enviar un mensaje a todos los usuarios suscritos.

    Params:
        message_text: Texto del mensaje a enviar.
    """
    for user_id in safe_users:
        telegram_bot.send_message(user_id, message_text)

def save_facial_recog_photo(message):
    """
    Función para registrar una foto de reconocimiento facial del usuario.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    telegram_bot.reply_to(
            message, "Proximamente!")

def usersExists():
    """
    Función para saber si existen usuarios registrados en el bot.

    Returns: Bool
    """
    return len(safe_users.keys()) > 0

def init():
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

    while True:
        telegram_bot.polling()
