# import cv2
# import base64
# from backend.utils.image_utils import base64_to_image

# # Read any image from disk (put a sample.jpg in project root)
# img = cv2.imread("sample.jpeg")

# # Encode to base64
# _, buffer = cv2.imencode(".jpg", img)
# base64_str = base64.b64encode(buffer).decode("utf-8")

# # Decode using our function
# decoded = base64_to_image(base64_str)

# if decoded is not None:
#     print("Image decoded:", decoded.shape)
# else:
#     print("Failed to decode image")


# import cv2
# from backend.services.face_service import get_face_embedding

# # Use a real face image
# img = cv2.imread("sample.jpeg")

# embedding = get_face_embedding(img)

# if embedding is not None:
#     print("Embedding shape:", embedding.shape)
# else:
#     print("No face detected")



import cv2
from backend.services.face_service import get_face_embedding
from backend.services.validation_service import calculate_similarity

# Load same image twice (for testing)
img1 = cv2.imread("sample.jpeg")
img2 = cv2.imread("sample.jpeg")

emb1 = get_face_embedding(img1)
emb2 = get_face_embedding(img2)

if emb1 is not None and emb2 is not None:
    score = calculate_similarity(emb1, emb2)
    print("Similarity score:", score)
else:
    print("Embedding failed")