# import requests
# import base64

# # Read image and convert to base64
# def encode_image(path):
#     with open(path, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")

# img_base64 = encode_image("sample.jpeg")

# payload = {
#     "image1": img_base64,
#     "image2": img_base64
# }

# response = requests.post("http://127.0.0.1:5000/verify-face", json=payload)

# print(response.json())


import requests
import base64

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


URL = "http://127.0.0.1:5000/verify-face"

# ---------------- TEST 1: ACCEPT ----------------
img1 = encode_image("/home/aki/EDGE/data/validation_set/person_1/img2.png")
img2 = encode_image("/home/aki/EDGE/data/validation_set/person_1/img5.png")

res = requests.post(URL, json={"image1": img1, "image2": img2})
print("ACCEPT TEST:", res.json())


# ---------------- TEST 2: REJECT ----------------
img1 = encode_image("/home/aki/EDGE/data/validation_set/person_1/img5.png")
img2 = encode_image("/home/aki/EDGE/data/validation_set/person_2/img4.png")

res = requests.post(URL, json={"image1": img1, "image2": img2})
print("REJECT TEST:", res.json())


# ---------------- TEST 3: PENDING ----------------
# Try same person but different conditions (pick distant images manually)
img1 = encode_image("/home/aki/EDGE/data/validation_set/person_3/img1.png")
img2 = encode_image("/home/aki/EDGE/data/validation_set/person_3/img3.png")

res = requests.post(URL, json={"image1": img1, "image2": img2})
print("PENDING TEST:", res.json())


# ---------------- TEST 4: RETRY ----------------
res = requests.post(URL, json={"image1": "", "image2": ""})
print("RETRY TEST:", res.json())