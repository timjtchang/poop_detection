import requests
import sys
import os

# Base URL of your Flask application
base_url = "http://localhost:5000"  # Adjust this if your server is running on a different address or port

def test_image_retrieval(image_name):
    url = f"{base_url}/getImage/{image_name}"
    print(url);
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Successfully retrieved image: {image_name}")
        # Save the image to a file
        with open(f"downloaded_{image_name}", "wb") as f:
            f.write(response.content)
        print(f"Image saved as downloaded_{image_name}")
    elif response.status_code == 404:
        print(f"Image not found: {image_name}")
        print(response.json())
    else:
        print(f"Unexpected error: Status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 getImage.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    print(f"Testing with image name: {image_name}")
    test_image_retrieval(image_name)