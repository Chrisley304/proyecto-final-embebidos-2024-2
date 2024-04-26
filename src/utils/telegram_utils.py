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
    with open('subscribed_users.json', 'r') as file:
        subscribed_users = json.load(file)
except FileNotFoundError:
    subscribed_users = []


def start(message):
    """
    Función para manejar el comando de inicio del bot.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    telegram_bot.reply_to(
        message, "¡Hola! Soy tu bot de seguridad. Usa /subscribe para recibir notificaciones de eventos.")


def subscribe(message):
    """
    Función para manejar la suscripción a las notificaciones.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = message.chat.id
    if user_id not in subscribed_users:
        subscribed_users.append(user_id)
        with open('subscribed_users.json', 'w') as file:
            json.dump(subscribed_users, file)
        telegram_bot.reply_to(
            message, "¡Te has suscrito satisfactoriamente! Ahora recibirás notificaciones de eventos.")
    else:
        telegram_bot.reply_to(message, "¡Ya estás suscrito!")


def unsubscribe(message):
    """
    Función para manejar la cancelación de la suscripción a las notificaciones.

    Params:
        message: Objeto de mensaje de Telegram.
    """
    user_id = message.chat.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        with open('subscribed_users.json', 'w') as file:
            json.dump(subscribed_users, file)
        telegram_bot.reply_to(
            message, "Te has desuscrito correctamente. Ya no recibirás notificaciones.")
    else:
        telegram_bot.reply_to(message, "No estás suscrito actualmente.")


def send_photo_to_subscribers(photo_path):
    """
    Función para enviar una foto a todos los usuarios suscritos.

    Params:
        photo_path: Ruta de la foto a enviar.
    """
    with open(photo_path, 'rb') as photo:
        for user_id in subscribed_users:
            telegram_bot.send_photo(user_id, photo)


def send_message_to_subscribers(message_text):
    """
    Función para enviar un mensaje a todos los usuarios suscritos.

    Params:
        message_text: Texto del mensaje a enviar.
    """
    for user_id in subscribed_users:
        telegram_bot.send_message(user_id, message_text)

# def something_happens():
    """
    Función de ejemplo para activar el envío de una foto.
    """
    # Tu lógica aquí para detectar un evento
    # Suponiendo que tienes una variable photo_path que contiene la ruta de la foto
    # send_photo_to_subscribers(photo_path)


def init():
    """
    Función para iniciar el bot de Telegram.
    """
    # Comandos del bot
    @telegram_bot.message_handler(commands=['start'])
    def handle_start(message):
        start(message)

    @telegram_bot.message_handler(commands=['subscribe'])
    def handle_subscribe(message):
        subscribe(message)

    @telegram_bot.message_handler(commands=['unsubscribe'])
    def handle_unsubscribe(message):
        unsubscribe(message)

    while True:
        telegram_bot.polling()
