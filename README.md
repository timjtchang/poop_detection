# Poop Detection Service

This service provides an API for detecting dog poop in images using machine learning.

## Demo

![Demo](docs/demo.gif)

## Setup

To set up and run the server, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/timjtchang/poop_detection.git
cd poop_detection
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows, use venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

4. Set up your Roboflow API key:
   - Sign up for a Roboflow account if you haven't already
   - Log in and visit `https://universe.roboflow.com/dog-poop/fake-dog-poop/model/1` to get your API_KEY
   - Clone the `.env.example` file to create a new `.env` file
   - Update the `.env` file with your Roboflow credentials:

```
API_KEY = "API_KEY_FOR_ROBOFLOW"
```

5. Run the Flask server:

```bash
flask run
```

The server should now be running on `http://localhost:5000`.

## Features

- Image upload for dog poop detection
- Real-time image processing and annotation
- Display of detection results with bounding boxes and confidence scores
- Automatic cleanup of processed images
- URL-based image detection API

## How to Use

1. Open a web browser and navigate to `http://localhost:5000`.
2. You'll see an upload form. Click "Choose File" to select an image from your computer.
3. After selecting an image, you'll see a preview of it on the page.
4. Click "Detect" to submit the image for processing.
5. The service will analyze the image and display the results, showing any detected dog poop with bounding boxes and confidence scores.
6. You can upload multiple images in succession.
7. The processed images are automatically deleted from the server when you navigate away from the results page.

## API Usage

The service also provides a URL-based API for dog poop detection:

1. Send a POST request to `http://localhost:5000/detect_url` with the image file in the request body.
2. The API will return a JSON response with the detection results.

**Example using Python requests:**

```python
import requests

url = 'http://localhost:5000/detect_url'
image_path = 'path/to/your/image.jpg'

with open(image_path, 'rb') as image_file:
    files = {'file': ('image.jpg', image_file, 'image/jpeg')}
    response = requests.post(url, files=files)

print(response.json())
```

**API Response:**

- If dog poop is detected:

  ```json
  {
    "ifwaste": 1,
    "data": [
      {
        "class": "dog poop",
        "confidence": 0.9,
        "x": 100,
        "y": 200,
        "width": 50,
        "height": 50
      }
    ],
    "image": "annotated_image_hash.jpg"
  }
  ```

- If no dog poop is detected:
  ```json
  {
    "ifwaste": 0,
    "data": [],
    "image": "annotated_image_hash.jpg"
  }
  ```

The `image` field contains the filename of the annotated image, which can be accessed at `http://localhost:5000/static/annotated_images/{image_filename}`.

**Note:** Ensure that your server is running and accessible at the specified URL before making API requests.

## Reference

https://universe.roboflow.com/dog-poop/fake-dog-poop/model/1

Note: This service is intended for demonstration purposes. The accuracy of detection may vary depending on the quality and content of the uploaded images.
