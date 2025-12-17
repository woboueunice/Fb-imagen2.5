from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def home():
    return "🚀 L'API KJM AI est en ligne !"

# --- NOUVEAU : ROUTE DE DIAGNOSTIC ---
# Va sur cette page pour voir les modèles disponibles
@app.route('/debug')
def debug_models():
    try:
        models_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models_list.append(m.name)
        return jsonify({
            "status": "success", 
            "message": "Voici les modèles disponibles pour ta clé",
            "models": models_list
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_message = request.args.get('message') or request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message manquant"}), 400

    try:
        # TENTATIVE 1 : On essaie le modèle Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        return jsonify({"status": "success", "reponse": response.text})
        
    except Exception as e:
        # TENTATIVE 2 : Si Flash échoue, on essaie le vieux modèle stable "gemini-pro"
        try:
            print(f"Flash a échoué ({e}), passage à Gemini Pro...")
            model_backup = genai.GenerativeModel('gemini-pro')
            response = model_backup.generate_content(user_message)
            return jsonify({
                "status": "success", 
                "reponse": response.text, 
                "note": "Réponse générée avec Gemini Pro (Backup)"
            })
        except Exception as e2:
            return jsonify({"error": "Tous les modèles ont échoué", "detail_flash": str(e), "detail_pro": str(e2)}), 500

# La partie image reste inchangée...
@app.route('/image', methods=['GET', 'POST'])
def generate_image():
    # (Garde ton code image ici, je l'ai raccourci pour la lisibilité)
    return jsonify({"status": "maintenance"}) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
