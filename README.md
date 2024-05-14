# Caja de seguridad Smart - Proyecto Final Embebidos 2024-2
 Repositorio donde se almacena el codigo del proyecto final de la materia Fundamentos de Sistemas Embebidos del semestre 2024-2.

## Como utilizar el repositorio

1. Instala las dependencias
```bash
pip install -r requirements.txt
```

2. Duplica el archivo `.env.example` y renombralo a `.env`, configurandolo con las variables de entorno necesarias (Notion & Telegram)
```bash
cp .env.example .env
```

3. Corre el script
```bash
python3 src/main.py
```

## Comandos de Telegram

- `/start`: Inicia el bot.
- `/veractividad`: Revisa la ultima actividad de la caja fuerte.
- `/reconocimientofacial`: Desbloquea la caja fuerte enviando una foto de tu cara.
- `/desbloqueomaestro`: Si tienes problemas con los sensores, utiliza tu contraseña maestra para abrirla.
- `/nuevorfid`: Una vez registrado, añade un tag RFID.
- `/nuevahuella`: Una vez registrado, añade una huella a la caja fuerte.
- `/nuevoreconocimientofacial`: Una vez registrado, envia una foto para añadirlo al reconocimiento facial.
- `/registro`: Una vez autorizado o primer usuario, registrate en el bot enviando tu nombre.
- `/solicitud`: Envia una solicitud a los "super usuarios" para tener permisos de interacción.
- `/revisarsolicitudes`: Revisa las solicitudes de personas para ser autorizadas.
- `/borrarperfil`: Elimina tu perfil del bot.
- `/ayuda`: Muestra información sobre el bot.

## Autores
- Christian Leyva
- Francisco Cardoso
- Oliver Alexis
