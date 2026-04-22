from flask import Blueprint, request, jsonify
from backend.utils.image_utils import base64_to_image
from backend.services.face_service import get_face_embedding
from backend.services.validation_service import calculate_similarity

verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/verify-face", methods=["POST"])
def verify_face():
    try:
        data = request.get_json()

        img1_base64 = data.get("image1")
        img2_base64 = data.get("image2")

        img1 = base64_to_image(img1_base64)
        img2 = base64_to_image(img2_base64)

        emb1 = get_face_embedding(img1)
        emb2 = get_face_embedding(img2)

        if emb1 is None or emb2 is None:
            return jsonify({"error": "Face not detected"}), 400

        score = calculate_similarity(emb1, emb2)

        return jsonify({"similarity_score": score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500