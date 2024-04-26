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


def add_log_entry_to_notion():

    log_date = datetime.now()
    try:
        response = notion_client.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            icon={
                "emoji": "🚨"
            },
            properties={
                "Nombre evento": {"title": [{"text": {"content": f"Prueba {log_date.strftime('%Y-%m-%d %H:%M:%S')}"}}]},
                "Tipo evento": {"multi_select": [{"name": "Prueba"}]},
                "Fecha evento": {"date": {"start": log_date.isoformat()}},
            },
        )
    except Exception as e:
        # APIResponseError
        print("Error: ", e)
