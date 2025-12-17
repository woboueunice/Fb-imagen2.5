from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import requests
import json
import base64
import re
from io import BytesIO
from gTTS import gTTS

app = Flask(__name__)

# --- CONFIGURATION ---
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def home():
    return "🚀 API KJM AI (Imagen 4.0 + Vocal) en ligne !"

# --- FONCTION VOIX ---
def text_to_audio_base64(text, lang='fr'):
    try:
        # Nettoyage basique du texte (retire les étoiles markdown)
        clean_text = re.sub(r'\*+', '', text)
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return base64.b64encode(audio_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"Erreur Audio: {e}")
        return None

# --- ENDPOINT CHAT (Texte + Vocal optionnel) ---
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_message = request.args.get('message') or request.json.get('message')
    vocal_mode = request.args.get('vocal') # &vocal=oui pour activer
    
    if not user_message: return jsonify({"error": "Message manquant"}), 400

    try:
        # On utilise le modèle standard 2.0 trouvé dans ta liste
        # Il est plus stable que le 2.5 qui t'a bloqué
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(user_message)
        reponse_texte = response.text

        result = {
            "status": "success",
            "type": "text",
            "model_used": "gemini-2.0-flash",
            "reponse": reponse_texte
        }

        # Génération Audio si demandé
        if vocal_mode == 'oui':
            audio_data = text_to_audio_base64(reponse_texte)
            if audio_data:
                result['audio_base64'] = audio_data
                result['audio_info'] = "Décoder le base64 en fichier MP3"

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Erreur Texte", "details": str(e)}), 500

# --- ENDPOINT IMAGE (VERSION IMAGEN 4.0) ---
@app.route('/image', methods=['GET', 'POST'])
def generate_image():
    prompt = request.args.get('prompt') or request.json.get('prompt')
    if not prompt: return jsonify({"error": "Prompt manquant"}), 400
    if not api_key: return jsonify({"error": "Clé API manquante"}), 500

    try:
        # MISE À JOUR MAJEURE : On pointe vers IMAGEN 4.0
        # C'est le modèle que nous avons vu dans ta liste 'models/imagen-4.0-generate-001'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1", # Tu peux changer en "16:9"
                "personGeneration": "allow_adult"
            }
        }
        
        # Envoi requête HTTP directe
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        
        if response.status_code != 200:
            return jsonify({"error": "Erreur Google Imagen 4", "code": response.status_code, "msg": response.text})

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
            return jsonify({"error": "Pas d'image", "debug": result})

    except Exception as e:
        return jsonify({"error": "Erreur système", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    
