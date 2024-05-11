# Caja de seguridad Smart - Proyecto Final Embebidos 2024-2
 Repositorio donde se almacena el codigo del proyecto final de la materia Fundamentos de Sistemas Embebidos del semestre 2024-2.

## Como utilizar el repositorio

1. Crea un `venv` en la carpeta del proyecto
```bash
python3 -m venv venv
```

2. Activa el `venv`
```bash
source venv/bin/activate
```

3. Instala las dependencias
```bash
pip install -r requirements.txt
```

4. Duplica el archivo `.env.example` y renombralo a `.env`, configurandolo con las variables de entorno necesarias (Notion & Telegram)
```bash
cp .env.example .env
```

5. Corre el script
```bash
python3 src/main.py
```

## Comandos de Telegram

- `/start`: Inicia el bot
- `/solicitud`: Envia una solicitud a los "super usuarios"
- `registro`: Una vez autorizado o primer usuario, registrate en el bot enviando tu nombre y una foto.
- `/nuevoreconocimientofacial`: Una vez registrado, envia una foto para añadirlo al reconocimiento facial.
- `/nuevahuella`: Una vez registrado, añade una huella al reconocimiento facial.
- `/nuevorfid`: Una vez registrado, añade un tag RFID.
- `/desbloquear`: Si tienes problemas con los sensores, utiliza tu contraseña maestra para abrirla.

## Autores
- Christian Leyva
- Francisco Cardoso
- Oliver Alexis