# ==============================================================================
# FLASK APPLICATION WITH MODEL INTEGRATION
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
from backend.waste_db import CLASS_LABELS, get_instructions


# --- Configuration ---
MODEL_PATH = 'smart_waste_model.h5' 
IMG_SIZE = (224, 224)
MODEL = None 

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable CORS for development (allows React on port 3000 to talk to Flask on 5000)
CORS(app) 

@app.route("/")
def home():
    return "Waste Classifier API running"

def load_and_prepare_model():
    """Loads the trained Keras model into memory once at startup."""
    global MODEL
    if MODEL is None:
        print("* Loading Keras model...")
        MODEL = load_model(MODEL_PATH) 
        # Crucial step to "warm up" the model for immediate predictions
        MODEL.predict(np.zeros((1, *IMG_SIZE, 3)))
        print("* Model loaded successfully!")

def preprocess_image(image_bytes):
    """Preprocesses raw image bytes for model prediction."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image)
    image_batch = np.expand_dims(image_array, axis=0)
    # Apply the MobileNetV2 scaling
    return preprocess_input(image_batch)

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for image upload and classification."""
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
                "instruction": disposal_info['instruction'],
                "tip": disposal_info['tip']
            })

        except Exception as e:
            # Log the error for debugging
            print(f"Prediction Error: {e}")
            return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def index():
    """Simple status check."""
    return jsonify({"status": "Smart Waste API is running", "model_loaded": MODEL is not None})

if __name__ == '__main__':
    load_and_prepare_model()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)