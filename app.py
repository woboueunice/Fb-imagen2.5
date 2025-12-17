from flask import Flask, jsonify
import os
import requests # On utilise requests pour contourner la vieille librairie

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def home():
    return "🔍 Outil de Diagnostic KJM AI"

@app.route('/check-models')
def check_models():
    if not api_key:
        return jsonify({"error": "Clé API manquante"}), 500

    # On demande la liste directement à l'API Google (REST)
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        all_models = data.get('models', [])
        
        # On va trier pour trouver ceux qui font des IMAGES
        image_models = []
        text_models = []
        
        for m in all_models:
            methods = m.get('supportedGenerationMethods', [])
            name = m.get('name')
            
            # Vérification si le modèle peut générer des images
            if 'generateImages' in methods or 'image' in name.lower():
                image_models.append({
                    "name": name,
                    "methods": methods
                })
            else:
                text_models.append(name)

        return jsonify({
            "status": "success",
            "AVAILABLE_IMAGE_MODELS": image_models,
            "available_text_models_sample": text_models[:5] # On en montre juste 5 pour pas polluer
        })

    except Exception as e:
        return jsonify({"error": "Erreur de connexion", "details": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
        
