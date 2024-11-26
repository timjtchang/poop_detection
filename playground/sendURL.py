import requests

url = 'http://127.0.0.1:5000/detect_url'
image_path = '../samples/shit1.jpg'

with open(image_path, 'rb') as image_file:
    files = {'file': ('image.jpg', image_file, 'image/jpeg')}
    response = requests.post(url, files=files)

print(response.json())