import os
import asyncio
import io
import edge_tts
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app) # Permite conexión desde GitHub Pages

# Configuración de API
client = OpenAI(
    api_key="sk-9o7PE0CVakwVWNVdK-vFZg", # Tu API Key
    base_url="https://api.totalgpt.ai/v1"
)

# El contenido de conocimiento.txt lo pegas aquí directamente para no subir archivos extra
CONOCIMIENTO = """
[PEGA AQUÍ TODO EL TEXTO DE TU ARCHIVO CONOCIMIENTO.TXT]
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pregunta = data.get("texto", "")
    
    mensajes = [
        {"role": "system", "content": f"Eres Asper-Bot. REGLAS: 1. Usa solo esto: {CONOCIMIENTO}. 2. Máximo 2 oraciones. 3. Si no sabes, di que no está en el catálogo 2026."},
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
        return jsonify({"respuesta": "Error en el servidor."}), 500

@app.route("/tts")
def tts():
    texto = request.args.get("texto", "")
    communicate = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
    
    async def get_audio():
        output = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output.write(chunk["data"])
        output.seek(0)
        return output

    audio_data = asyncio.run(get_audio())
    return send_file(audio_data, mimetype="audio/mp3")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)