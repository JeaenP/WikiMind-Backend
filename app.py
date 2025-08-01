from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import re

app = Flask(__name__)
CORS(app)

# Configura tu API key de Gemini
genai.configure(api_key="API_KEY")
modelo_general = genai.GenerativeModel('gemini-pro')
modelo_flash = genai.GenerativeModel('gemini-2.0-flash-exp')

@app.route('/resumen_con_estilo', methods=['POST'])
def generar_resumen_estilizado():
    data = request.json
    etiqueta = data.get('label', 'Recurso desconocido')
    uri = data.get('uri', '')

    propiedades = [str(p) for p in data.get('propiedades', []) if isinstance(p, str) and p.strip()]

    prompt = f"""
Eres un asistente que genera resúmenes educativos para estudiantes. El recurso se llama "{etiqueta}" y su identificador es "{uri}". Aquí están las propiedades relacionadas:

{chr(10).join(propiedades)}

Genera un texto descriptivo como si fuera un resumen introductorio al estilo Wikipedia, incluyendo enlaces internos en formato markdown como:
**[Nombre del recurso](URI)** o **[etiqueta](#idInterno)** si es algo interno.

Destaca lo más relevante y escribe de forma clara y atractiva. Usa máximo 3 párrafos. Evita redundancia. Sé creativo, pero riguroso.
"""

    try:
        response = modelo_flash.generate_content(prompt)
        return jsonify({"resumen": response.text})
    except Exception as e:
        print("❌ Error generando resumen:", str(e))
        return jsonify({"resumen": "", "error": "Error generando resumen"}), 500

@app.route('/filtrar-propiedades', methods=['POST'])
def filtrar_propiedades():
    data = request.json
    propiedades = data.get("propiedades", [])

    prompt = f""" 
    
    Eres un asistente que filtra propiedades RDF educativas para una trivia visual.

    Dado el siguiente array de propiedades en formato JSON, selecciona de 1 a 10 que consideres más educativas o útiles para crear trivias visuales.

    Devuelve SOLO un JSON con el siguiente formato exacto (sin texto fuera del JSON):

    {{
    "propiedades": [
        "URI_1",
        "URI_2",
        ...
    ]
    }}

    Ejemplo:

    Entrada:
    [
    {{
        "propiedad": "http://www.w3.org/2000/01/rdf-schema#label",
        "valor": "Egipto"
    }},
    ...
    ]

    Ahora, filtra las propiedades de esta entrada:

    {propiedades}

    """

    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)

    print(response.text)

    match = re.search(r'\{[\s\S]*\}', response.text)
    if not match:
        print("❌ No se encontró JSON en la respuesta de Gemini:", response.text)
        return jsonify({
            "propiedades": [],
            "error": "Respuesta malformada de Gemini"
        }), 500

    try:
        resultado = json.loads(match.group())
        return jsonify(resultado)
    except Exception as e:
        print("❌ Error al parsear JSON:", match.group())
        return jsonify({
            "propiedades": [],
            "error": "Error al parsear JSON"
        }), 500
    


