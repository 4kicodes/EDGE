from insightface.app import FaceAnalysis

# Load model once (global)
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0)

def detect_faces(image):
    try:
        faces = face_app.get(image)
        return faces
    except Exception as e:
        print("Face detection error:", str(e))
        return []
    

def get_face_embedding(image):
    try:
        faces = detect_faces(image)

        if len(faces) == 0:
            return None

        # Take first detected face
        face = faces[0]

        embedding = face.embedding
        return embedding
    except Exception as e:
        print("Embedding error:", str(e))
        return None
    

