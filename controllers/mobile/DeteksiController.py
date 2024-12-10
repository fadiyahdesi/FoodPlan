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
def predict(files):
    try:
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        results = []

        # Validasi dan proses setiap file
        for file in files:
            if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                results.append({'filename': file.filename, 'error': 'Invalid file type. Please upload PNG, JPG, or JPEG.'})
                continue

            # Simpan file sementara
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)
            img_path = os.path.join(upload_folder, file.filename)
            file.save(img_path)
            logger.info(f"Image saved at {img_path}")

            try:
                # Prediksi kelas gambar
                predicted_class = predict_image(img_path)
                results.append({'filename': file.filename, 'prediction': predicted_class})
            except Exception as e:
                results.append({'filename': file.filename, 'error': str(e)})
            finally:
                os.remove(img_path)  # Hapus file setelah diproses

        return results
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise ValueError(f"Error: {str(e)}")
