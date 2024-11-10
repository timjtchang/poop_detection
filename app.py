from flask import Flask, request, jsonify, render_template
from roboflow import Roboflow
import supervision as sv
import cv2
import os
import hashlib
import time
import numpy as np
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
API_KEY = os.getenv("API_KEY")

RESULT_IMAGE_ADDRESS = 'static/'

# Define the static folder and ensure it exists
static_folder = 'static'
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# Define a specific folder for annotated images within the static folder
annotated_folder = os.path.join(static_folder, 'annotated_images')
if not os.path.exists(annotated_folder):
    os.makedirs(annotated_folder)

app = Flask(__name__, static_folder=static_folder)

# Initialize Roboflow
rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project("fake-dog-poop")
model = project.version(1).model

# Initialize annotators
label_annotator = sv.LabelAnnotator()
bounding_box_annotator = sv.BoxAnnotator()

def generate_file_hash(filename):
    digest = hashlib.sha256()
    timestamp = str(int(time.time()))
    combined = f"{filename}_{timestamp}"
    digest.update(combined.encode())
    return digest.hexdigest()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/delete-annotated-image', methods=['POST'])
def delete_annotated_image():
    data = request.get_json()
    filename = data.get('filename')
    
    if filename:
        file_path = os.path.join(app.static_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': 'File deleted successfully'}), 200
    return jsonify({'message': 'File not found'}), 404

@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            # Read the file directly into memory
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise FileNotFoundError("Image could not be read")
            
            # Save the image temporarily for Roboflow prediction
            temp_filename = f"temp_{generate_file_hash(file.filename)}.jpg"
            temp_filepath = os.path.join(static_folder, temp_filename)
            cv2.imwrite(temp_filepath, image)
            
            result = model.predict(temp_filepath, confidence=15, overlap=30).json()
            
            # Delete the temporary file
            os.remove(temp_filepath)
            
            labels = [item["class"] for item in result["predictions"]]
            detections = sv.Detections.from_inference(result)
            
            # Annotate the image
            annotated_image = bounding_box_annotator.annotate(
                scene=image, detections=detections)
            annotated_image = label_annotator.annotate(
                scene=annotated_image, detections=detections, labels=labels)
            
            # Generate a hash for the filename
            file_hash = generate_file_hash(file.filename)

            # Save the annotated image in the static folder using the hash
            output_filename = f"{file_hash}.jpg"
            output_path = os.path.join(annotated_folder, output_filename)
            cv2.imwrite(output_path, annotated_image)

            return render_template('result.html', 
                                annotated_image=f"annotated_images/{output_filename}",
                                detections=result["predictions"])
            
        except Exception as e:
            return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)