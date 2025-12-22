# ==============================================================================
# FLASK APPLICATION WITH MODEL INTEGRATION (PRODUCTION READY)
# ==============================================================================
import os
import io
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input 

from waste_db import CLASS_LABELS, get_instructions

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'smart_waste_model.h5')
IMG_SIZE = (224, 224)
MODEL = None 

# --- Flask App Initialization ---
app = Flask(__name__)

# Updated CORS to be more explicit for web deployments
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://smart-waste-classifier-rust.vercel.app", # Removed trailing slash
            "http://localhost:3000"
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def load_and_prepare_model():
    """Loads the trained Keras model into memory."""
    global MODEL
    if MODEL is None:
        try:
            print("* Loading Keras model...")
            # Use compile=False to avoid errors if custom metrics were used during training
            MODEL = load_model(MODEL_PATH, compile=False) 
            # Warm up the model with a dummy prediction
            MODEL.predict(np.zeros((1, *IMG_SIZE, 3)))
            print("* Model loaded successfully!")
        except Exception as e:
            print(f"* Error loading model: {e}")

# IMPORTANT: Load the model here so Gunicorn catches it
load_and_prepare_model()

def preprocess_image(image_bytes):
    """Preprocesses raw image bytes for model prediction."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image)
    image_batch = np.expand_dims(image_array, axis=0)
    return preprocess_input(image_batch)

# --- Routes ---

@app.route("/", methods=['GET'])
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "Waste Classifier API is running",
        "model_loaded": MODEL is not None,
        "environment": "Render/Production"
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for image upload and classification."""
    if MODEL is None:
        return jsonify({'error': 'Model not loaded on server'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['file']
    
    if file:
        try:
            # 1. Preprocess
            image_bytes = file.read()
            processed_image = preprocess_image(image_bytes)

            # 2. Predict
            predictions = MODEL.predict(processed_image)
            predicted_index = np.argmax(predictions, axis=1)[0]
            confidence = float(predictions[0][predicted_index])
            predicted_class = CLASS_LABELS.get(predicted_index, 'unknown')
            
            # 3. Get Instructions
            disposal_info = get_instructions(predicted_class)
            
            # 4. Return JSON Response
            return jsonify({
                "class": predicted_class,
                "confidence": round(confidence, 4),
                "instruction": disposal_info.get('instruction', 'No instructions found.'),
                "tip": disposal_info.get('tip', 'No tips found.')
            })

        except Exception as e:
            print(f"Prediction Error: {e}")
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# This is only used when running locally: python app.py
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)