import discord
import openai
import os
import json
import socket
import sys

# ---- CONFIGURACIÓN ----
DISCORD_TOKEN = "DISCORD_TOKEN"
OPENAI_API_KEY = "OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ---- ARCHIVO DE HISTORIAL ----
ARCHIVO_HISTORIAL = "historial.json"

def cargar_historial():
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def guardar_historial(historial):
    with open(ARCHIVO_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)

# ---- FUNCION PARA CHEQUEAR INTERNET ----
def comprobar_internet(host="discord.com", port=443, timeout=5):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# ---- PERSONALIDAD ----
PERSONALIDAD = """
Eres Bytrax, un bot que es algo serio, eres de chile amigo de fakiller, fa, ignkxller que son muy cercanos.
Siempre respondes de forma neutral, casi no agregas emojis, pero cuando se trata de tu amigo siempre pones estos emojis 😍😘♥🥰, 
te gusta jugar minecraft cubecraft bedrock en ctf (capture the flag), también juegas scrims con tus amigos hymahe, kanochi, nezo, juano, chris, chavy, fa o fakiller, y head, 
también les pides jugar a ellos partidas 2v2 o roblox, te gusta jugar en un juego llamado Volleyball Legends, casi siempre cuando te hablan dices que, eres de pocas palabras.
Casi siempre demuestras tu amor por tu amigo fakiller, debes decirle a los demás usuarios cuando quieras jugar que saquen "nombre del juego" y hablas con un tono chileno al escribir.
"""

# ---- CARGAR HISTORIAL ----
historial_usuarios = cargar_historial()

# ---- EVENTOS ----
@client.event
async def on_ready():
    print(f"{client.user} está conectado y listo!")

@client.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == client.user:
        return

    # Revisar si el bot fue mencionado o es DM
    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        usuario = str(message.author.id)

        # Iniciar historial si es la primera vez que habla
        if usuario not in historial_usuarios:
            historial_usuarios[usuario] = []

        # Guardar el mensaje del usuario
        historial_usuarios[usuario].append(f"Usuario: {message.content}")

        # Crear prompt para IA con TODO el historial (infinito)
        prompt = PERSONALIDAD + "\n" + "\n".join(historial_usuarios[usuario]) + "\nBot:"

        # Llamada a OpenAI
        try:
            respuesta = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.8
            )
            texto_respuesta = respuesta.choices[0].text.strip()
        except Exception as e:
            texto_respuesta = "¡Ups! No pude conectarme a OpenAI. 😅"

        # Guardar respuesta del bot en historial
        historial_usuarios[usuario].append(f"Bot: {texto_respuesta}")

        # Guardar historial en archivo JSON
        guardar_historial(historial_usuarios)

        # Enviar respuesta al canal
        await message.channel.send(texto_respuesta)

# ---- INICIAR BOT ----
if not comprobar_internet():
    print("❌ No hay conexión a Internet o problema de DNS. Revisa tu red.")
    sys.exit()

try:
    client.run(DISCORD_TOKEN)
except Exception as e:
    print(f"❌ Error al iniciar el bot: {e}")

