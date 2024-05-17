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

    if event_type == "Intento apertura 🚨":
        emoji = "🚨"
    elif event_type == "Apertura ✅":
        emoji = "✅" 

    try:
        response = notion_client.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            icon={
                "emoji": emoji
            },
            properties={
                "Nombre evento": {"title": [{"text": {"content": f"{event_type}: {user_name} a las {log_date.strftime('%Y-%m-%d %H:%M:%S')}"}}]},
                "Tipo evento": {"select": {"name": event_type}},
                "Fecha evento": {"date": {"start": log_date.isoformat()}},
                "Usuario": {"select": {"name": user_name}},
                "Medio desbloqueo": {"multi_select": [{"name": unlock_type}]}
            },
        )
    except Exception as e:
        # APIResponseError
        print("Error: ", e)

def get_last_n_events(n_events) -> list[str]:
    """
        Funcion para obtener los ultimos n eventos de la caja de seguridad registrados en el log de Notion.

        Params:
            n_events: Numero de ultimos eventos que se desean obtener.

        Returns:
            list[str]: Lista de strings con mensajes a mostrar en Telegram.
    """

    try:
        response = notion_client.databases.query(
            database_id=NOTION_DATABASE_ID,
            page_size=n_events,
            sorts=[
                {
                    "property": "Fecha evento",
                    "direction": "descending"
                }
            ]
        )

        if response:
            results = response["results"]
            
            if len(results) > 0:
                messages = []

                for result in results:
                    result_properties = result["properties"]
                    result_type_event = result_properties["Tipo evento"]["select"]["name"]
                    result_user = result_properties["Usuario"]["select"]["name"]
                    result_unlock_types = "".join(unlock["name"] for unlock in result_properties["Medio desbloqueo"]["multi_select"])
                    result_date = result_properties["Fecha evento"]["date"]["start"]
                    result_date_formatted = datetime.fromisoformat(result_date).strftime("%d/%m/%Y - %I:%M:%S %p")

                    formatedResult = f"**{result_type_event}**\n👤**Usuario:** {result_user}\n🔑**Medio/s:** {result_unlock_types}\n⏰**Fecha y hora:** {result_date_formatted}"

                    messages.append(formatedResult)

                return messages
            else:
                return ["No hay eventos para mostrar"]

    except Exception as e:
        # APIResponseError
        print("Error: ", e)
        return ["Ocurrio un error al mostrar los eventos, intente mas tarde"]