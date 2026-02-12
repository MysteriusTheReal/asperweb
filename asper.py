import os
import asyncio
import io
import edge_tts
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app) 

# Configuración de API
client = OpenAI(
    api_key="sk-9o7PE0CVakwVWNVdK-vFZg", 
    base_url="https://api.totalgpt.ai/v1"
)

# --- REEMPLAZA ESTO CON TU TEXTO REAL ---
CONOCIMIENTO = """
[PEGA AQUÍ TODO EL TEXTO DE TU ARCHIVO CONOCIMIENTO.TXT]
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pregunta = data.get("texto", "")
    
    # Prompt optimizado
    mensajes = [
        {"role": "system", "content": f"Eres Asper-Bot, asistente del TecNM Iztapalapa III. Reglas: 1. Usa solo esta info: {CONOCIMIENTO}. 2. Sé breve (máximo 2 oraciones). 3. Si no sabes algo, di que no está en el catálogo 2026."},
        {"role": "user", "content": pregunta}
    ]

    try:
        response = client.chat.completions.create(
            model="Sao10K-L3.3-70B-Euryale-v2.3-FP8-Dynamic",
            messages=mensajes,
            temperature=0.0
        )
        respuesta = response.choices[0].message.content.strip()
        return jsonify({"respuesta": respuesta})
    except Exception as e:
        print(f"Error IA: {e}")
        return jsonify({"respuesta": "Lo siento, tuve un problema al conectar con mi cerebro artificial."}), 500

@app.route("/tts")
def tts():
    texto = request.args.get("texto", "")
    if not texto:
        return "No text provided", 400

    async def get_audio():
        communicate = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
        output = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output.write(chunk["data"])
        output.seek(0)
        return output

    try:
        # Forma más segura de correr asyncio en Flask
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(get_audio())
        loop.close()
        return send_file(audio_data, mimetype="audio/mp3")
    except Exception as e:
        print(f"Error TTS: {e}")
        return "Error generating audio", 500

# Ruta de prueba para saber si el servidor está vivo
@app.route("/")
def health_check():
    return "Asper-Bot API está en línea y escuchando."

if __name__ == "__main__":
    # Esto solo se usa para pruebas locales
    app.run(host="0.0.0.0", port=10000)
