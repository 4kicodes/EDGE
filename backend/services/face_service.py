from insightface.app import FaceAnalysis

# Load model once (global)
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0)

def detect_faces(image):
    try:
        faces = face_app.get(image)

        if len(faces) == 0:
            return "NO_FACE", []

        if len(faces) > 1:
            return "MULTIPLE_FACES", faces

        return "OK", faces

    except Exception as e:
        print("Face detection error:", str(e))
        return "ERROR", []
    

def get_face_embedding(image):
    try:
        status, faces = detect_faces(image)

        if status == "NO_FACE":
            return "NO_FACE", None

        if status == "MULTIPLE_FACES":
            return "MULTIPLE_FACES", None

        if status != "OK":
            return "ERROR", None

        # Exactly one face
        face = faces[0]
        embedding = face.embedding

        return "OK", embedding

    except Exception as e:
        print("Embedding error:", str(e))
        return "ERROR", None
    

