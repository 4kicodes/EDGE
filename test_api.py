import requests
import base64

# Read image and convert to base64
def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

img_base64 = encode_image("sample.jpeg")

payload = {
    "image1": img_base64,
    "image2": img_base64
}

response = requests.post("http://127.0.0.1:5000/verify-face", json=payload)

print(response.json())