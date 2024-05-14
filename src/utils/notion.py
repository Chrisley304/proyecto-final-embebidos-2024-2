import os
from dotenv import load_dotenv
from datetime import datetime
from notion_client import Client

# Carga de tokens API desde archivo .env
load_dotenv()
NOTION_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
# Inicialización de cliente de Notion utilizando el token API
notion_client = Client(auth=NOTION_TOKEN)


def add_log_entry_to_notion(user_name, event_type, log_date, unlock_type):
    """
        Funcion para añadir a la db de Notion el registro de las aperturas o intentos de aperturas de la caja fuerte.

        Params:
            user_name: Nombre del usuario (si se conoce)
            event_type: Tipo de evento
            log_date: Fecha del evento
            unlock_type: Medio por el cual se desbloqueo/intento desbloquear.
    """

    emoji = "🚨"

    if event_type == "Intento apertura":
        emoji = "🚨"
    elif event_type == "Apertura":
        emoji = "✅" 

    try:
        response = notion_client.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            icon={
                "emoji": emoji
            },
            properties={
                "Nombre evento": {"title": [{"text": {"content": f"{event_type}: {user_name} a las {log_date.strftime('%Y-%m-%d %H:%M:%S')}"}}]},
                "Tipo evento": {"multi_select": [{"name": event_type}]},
                "Fecha evento": {"date": {"start": log_date.isoformat()}},
                "Usuario": {"select": {"name": user_name}},
                "Medio desbloqueo": {"select": {"name": unlock_type}}
            },
        )
    except Exception as e:
        # APIResponseError
        print("Error: ", e)
