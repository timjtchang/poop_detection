from flask import Flask, request, jsonify, render_template, send_file
from roboflow import Roboflow
import supervision as sv
import cv2
import os
import hashlib
import time
import json
import numpy as np
import requests
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

def detect(file):
    if file.filename == '':
        return 'No selected file'
    
    if file:
        try:
            # Read the file directly into memory
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return 'no image'
            
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

            return [output_filename, result["predictions"] ]
            
        except Exception as e:
            return e

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

@app.route('/detect_url', methods=['POST'])
def detect_url():
    print("hello")
    # Check for the presence of required files and parameters
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    print(latitude, ", ", longitude)
    
    # Validate latitude and longitude
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    try:
        # Attempt to convert latitude and longitude to floats
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'Invalid latitude or longitude'}), 400

    result = detect(file)
    print(result)
    print(f"Latitude: {latitude}, Longitude: {longitude}")

    if isinstance(result, list):
        if len(result[1]) > 0:
            # Waste detected, send data to ThingsBoard
            url = "http://44.244.136.206:8080/api/v1/CEqOvwwvX7qojLWjDS0v/telemetry"
            headers = {"Content-Type": "application/json"}
            ts = int(time.time() * 1000)  # Current timestamp in milliseconds
            data = json.dumps({
                "ts": ts,
                "latitude": latitude,
                "longitude": longitude
            })

            try:
                resp = requests.post(url, headers=headers, data=data)
                resp.raise_for_status()  # Raise an exception for HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Error sending data to ThingsBoard: {e}")

            return jsonify({'ifwaste': 1, 'data': result[1], 'image': result[0], 'latitude': latitude, 'longitude': longitude}), 200
        else:
            return jsonify({'ifwaste': 0, 'data': result[1], 'image': result[0], 'latitude': latitude, 'longitude': longitude}), 200
    elif result == 'no file':
        return jsonify({'error': 'No file part'}), 400
    elif result == 'No selected file':
        return jsonify({'error': 'No selected file'}), 400
    elif result == 'no image':
        return jsonify({'error': 'Image could not be read'}), 400
    elif isinstance(result, Exception):
        return jsonify({'error': 'Server issues'}), 402





@app.route('/detect', methods=['POST'])
def detect_ui():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    result = detect(file)

    if isinstance(result, list):
        return render_template('result.html', 
                    annotated_image=f"annotated_images/{result[0]}",
                    detections=result[1])
    elif(result == 'no file'):
        return jsonify({'error': 'No file part'}), 400
    elif( result == 'No selected file'):
        return jsonify({'error': 'No selected file'}), 400
    elif( result == 'no image'):
        return jsonify({'error': 'Image Could not read'}), 400
    elif( result is Exception ):
        return render_template('error.html', error=str(result)), 500
    

@app.route('/getImage/<string:image_name>', methods=['GET'])
def getImage(image_name):

    print('hello')
    # Define the directory where your images are stored
    image_directory = 'static/annotated_images'
    
    # Construct the full path to the requested image
    image_path = os.path.join(image_directory, image_name)
    
    # Check if the file exists
    if os.path.isfile(image_path):
        # Determine the MIME type based on the file extension
        _, ext = os.path.splitext(image_name)
        mime_type = 'image/jpeg' if ext.lower() in ['.jpg', '.jpeg'] else 'image/png'
        
        # Return the image file
        return send_file(image_path, mimetype=mime_type)
    else:
        return jsonify({'error': 'Image Not Exist'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)