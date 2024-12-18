import requests

# Define the endpoint URL
url = "http://127.0.0.1:5000/detect_url"

# File path to test image
file_path = "../samples/shit1.jpg"

# Define the latitude and longitude
latitude = 34.0522
longitude = -118.2437

# Prepare the payload
files = {'file': open(file_path, 'rb')}
data = {'latitude': latitude, 'longitude': longitude}

# Send the POST request
try:
    response = requests.post(url, files=files, data=data)

    # Print the response from the server
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json())
except Exception as e:
    print("An error occurred:", str(e))
