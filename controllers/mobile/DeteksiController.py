from flask import request
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the pre-trained model
MODEL_PATH = 'data/vgg16_model.h5'
LABELS_PATH = 'data/labels.txt'

# Validasi path model
if not os.path.exists(MODEL_PATH):
    logger.error(f"Model file not found at {MODEL_PATH}")
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

if not os.path.exists(LABELS_PATH):
    logger.error(f"Labels file not found at {LABELS_PATH}")
    raise FileNotFoundError(f"Labels file not found at {LABELS_PATH}")

model = load_model(MODEL_PATH)

# Define image size
IMG_SIZE = (224, 224)  # Sesuaikan dengan input size model (224x224x3)

# Load class names from the 'labels.txt' file
def load_class_names(file_path):
    with open(file_path, 'r') as f:
        class_names = [line.strip() for line in f.readlines()]
    return class_names

# Load nama kelas dari file labels.txt
class_names = load_class_names(LABELS_PATH)

# Function to process uploaded image and make prediction
def predict_image(img_path):
    try:
        # Load and preprocess the image
        img = image.load_img(img_path, target_size=IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalisasi

        # Make prediction
        prediction = model.predict(img_array)
        predicted_class_idx = np.argmax(prediction, axis=1)[0]

        # Return the class name based on predicted class index
        predicted_class = class_names[predicted_class_idx]
        return predicted_class
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise ValueError(f"Error during prediction: {str(e)}")

# Function to handle prediction from Flask endpoint
def predict():
    try:
        # Check if the file is in the request
        if 'file' not in request.files:
            return 'Error: No file part in the request.'
        file = request.files['file']
        if file.filename == '':
            return 'Error: No selected file.'

        # Validasi ekstensi file
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            return 'Error: Invalid file type. Please upload a PNG, JPG, or JPEG file.'

        # Make sure the 'uploads' directory exists
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)  # Create the uploads folder if it doesn't exist

        # Save the uploaded image temporarily
        img_path = os.path.join(upload_folder, file.filename)
        file.save(img_path)
        logger.info(f"Image saved at {img_path}")

        # Predict the class of the uploaded image
        predicted_class = predict_image(img_path)

        # Optionally delete the uploaded file after processing
        os.remove(img_path)

        # Return the result with the class name
        return predicted_class
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
