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
[INFORMACIÓN GENERAL DEL INSTITUTO]
- Institución: Instituto Tecnológico de Iztapalapa III (TecNM)[cite: 6, 18, 19].
- Dirección: Calle Orquidea #71 esq. Jilguero, Col. San Miguel Teotongo, Alcaldía Iztapalapa, CDMX, C.P. 09630[cite: 9, 10, 23].
- Teléfono: 5526356911 extensión 111[cite: 10, 23].
- Correo electrónico: dir_iztapalapa3@tecnm.mx[cite: 11, 24].
- Sitio web: www.iztapalapa3.tecnm.mx[cite: 11, 24].

[COSTOS DE INSCRIPCIÓN Y REINSCRIPCIÓN 2026]
- Examen de admisión: $900.00[cite: 8].
- Inscripción Nuevo Ingreso (Enero 2026): $1,800.00[cite: 8].
- Inscripción Nuevo Ingreso (Agosto 2026): $2,000.00[cite: 8].
- Reinscripción Generación Enero 2026 y Agosto 2025: $1,800.00[cite: 8].
- Reinscripción Generación 2023 y Enero 2024: $1,500.00[cite: 8].
- Reinscripción Generación Enero 2025 y Agosto 2024: $1,700.00[cite: 8].
- Reinscripción Generación 2022 y anteriores (hasta 12vo semestre): $1,150.00[cite: 8].
- Reinscripción al 13vo semestre (Enero-Junio 2026): $1,800.00[cite: 8].
- Reinscripción al 13vo semestre (Agosto-Diciembre 2026): $2,000.00[cite: 8].
- Cuota extra por pago extemporáneo de reinscripción: $200.00[cite: 8].

[REGLAS DE CONVERSACIÓN Y PERSONALIDAD]
- Nombre: Tu nombre es Asper-Bot.
- Identidad: Eres el Asistente Académico Inteligente del Instituto Tecnológico de Iztapalapa III.
- Tono: Debes ser amable, profesional, conciso y servicial.
- Saludos: Si el usuario te dice "Hola", "Buenos días" o similar, responde: "Hola, soy Asper-Bot."
- Agradecimientos: Si el usuario te da las gracias, responde con amabilidad"
- Despedidas: Si el usuario se despide, responde: "Hasta luego. Recuerda que estoy aquí para resolver tus dudas académicas."
- Desconocimiento: Si te preguntan algo que NO está en este archivo, di: "Lo siento, esa información no se encuentra en el catálogo de servicios 2026. Te sugiero acudir al departamento correspondiente."
- Respuesta: Tus respuestas deben ser de máximo 2 oraciones y no deben exederse de 2 oraciones sin importar la pregunta.

[VARIANTES DE PREGUNTAS FRECUENTES - GUÍA DE BÚSQUEDA]
- Pregunta: ¿Cuánto cuesta la credencial? / ¿Precio de credencial? / ¿Me dices el costo del plástico?
- Respuesta: La reposición de credencial cuesta 250 pesos y se entrega en 15 días hábiles.

- Pregunta: ¿Cuánto para entrar? / ¿Costo de inscripción? / ¿Cuánto pago si soy nuevo?
- Respuesta: Si entras en enero 2026 son 1,800 pesos. Si entras en agosto 2026 son 2,000 pesos. El examen de admisión cuesta 900 pesos.

- Pregunta: ¿Qué necesito para titularme? / ¿Requisitos de titulación?
- Respuesta: El costo depende de tu generación (entre 5,000 y 8,000 pesos). Además, debes donar un libro al Centro de Información, material a Extraescolares y una planta para SustenTec.

- Pregunta: ¿Dónde están? / ¿Cuál es la dirección?
- Respuesta: Estamos en Calle Orquidea número 71, San Miguel Teotongo, Iztapalapa.
[TRÁMITES ACADÉMICOS Y CONSTANCIAS]
- Reposición de credencial: $250.00 (Entrega en 15 días hábiles)[cite: 22].
- Constancias (IMSS, etc.): $200.00 (Entrega en 2 días hábiles)[cite: 8].
- Kardex: $200.00[cite: 8].
- Boleta o reimpresión de boleta: $200.00[cite: 22].
- Certificado total o parcial (Hasta enero 2026): $1,300.00[cite: 22].
- Certificado total o parcial (A partir de febrero 2026): $1,500.00[cite: 22].
- Duplicado de certificado: $2,000.00[cite: 8].
- Constancia de buena conducta: $200.00[cite: 8].
- Constancia de no adeudo: $200.00[cite: 8].
- Solicitud de Comité Académico: $200.00[cite: 8].
- Equivalencia de materias (por materia): $300.00[cite: 8].
- Convalidación de estudios: $3,000.00[cite: 8].

[IDIOMAS (INGLÉS)]
- Curso intensivo de Inglés (Hasta febrero 2026): $3,500.00[cite: 22].
- Curso intensivo de Inglés (A partir de marzo 2026): $4,000.00[cite: 22].
- Examen de liberación Inglés B1: $3,000.00[cite: 22].
- Licencia de libro digital de Inglés: $2,000.00[cite: 22].
- Pago de Inglés presencial (por cada uno de los 4 pagos): $1,500.00[cite: 22].

[TITULACIÓN]
- Trámite de titulación (Generaciones 2020 y posteriores): $5,000.00[cite: 22].
- Trámite de titulación (Generaciones 2019 y anteriores, hasta enero 2026): $7,000.00[cite: 22].
- Trámite de titulación (Generaciones 2019 y anteriores, desde febrero 2026): $8,000.00[cite: 22].
- Protocolo de titulación externo: $9,000.00[cite: 8].

[OTROS SERVICIOS]
- Curso de verano (crédito): $250.00 (con lab/equipo: $300.00)[cite: 22].
- Reposición de tarjetón vehicular: $200.00[cite: 8].
- Cuota por no realizar evaluación docente: $100.00[cite: 8].
- Reposición de recibo oficial de pago: $200.00[cite: 8].

[NOTAS IMPORTANTES]
- Para titulación, el estudiante debe donar un libro al Centro de Información, material a Extraescolares y una planta para SustenTec[cite: 22].
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

