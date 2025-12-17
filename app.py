from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import requests
import json

app = Flask(__name__)

# --- CONFIGURATION ---
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def home():
    return "🚀 API KJM AI (Texte + Imagen 4.0) est en ligne !"

# --- ENDPOINT CHAT (Texte uniquement) ---
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_message = request.args.get('message') or request.json.get('message')
    
    if not user_message: return jsonify({"error": "Message manquant"}), 400

    try:
        # On utilise le modèle STABLE Gemini 2.0 Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(user_message)
        
        return jsonify({
            "status": "success",
            "type": "text",
            "model_used": "gemini-2.0-flash",
            "reponse": response.text
        })

    except Exception as e:
        return jsonify({"error": "Erreur Chat", "details": str(e)}), 500

# --- ENDPOINT IMAGE (Imagen 4.0) ---
@app.route('/image', methods=['GET', 'POST'])
def generate_image():
    prompt = request.args.get('prompt') or request.json.get('prompt')
    if not prompt: return jsonify({"error": "Prompt manquant"}), 400
    if not api_key: return jsonify({"error": "Clé API manquante"}), 500

    try:
        # Connexion directe à IMAGEN 4.0 (Ta version exclusive)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1", 
                "personGeneration": "allow_adult"
            }
        }
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        
        if response.status_code != 200:
            return jsonify({"error": "Erreur Google Imagen", "code": response.status_code, "msg": response.text})

        result = response.json()
        
        if 'predictions' in result and result['predictions']:
            base64_data = result['predictions'][0]['bytesBase64Encoded']
            return jsonify({
                "status": "success",
                "model_used": "imagen-4.0-generate-001",
                "type": "image_base64", 
                "data": base64_data
            })
        else:
            return jsonify({"error": "Pas d'image générée", "debug": result})

    except Exception as e:
        return jsonify({"error": "Erreur système", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
