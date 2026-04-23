from flask import Blueprint, request, jsonify
from backend.utils.image_utils import base64_to_image
from backend.services.face_service import get_face_embedding
from backend.services.validation_service import calculate_similarity, make_decision
from backend.utils.logger import log_event

verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/verify-face", methods=["POST"])
def verify_face():
    try:
        data = request.get_json()

        img1_base64 = data.get("image1")
        img2_base64 = data.get("image2")

        img1 = base64_to_image(img1_base64)
        img2 = base64_to_image(img2_base64)

        status1, emb1 = get_face_embedding(img1)
        status2, emb2 = get_face_embedding(img2)

        # Handle edge cases
        if status1 == "NO_FACE" or status2 == "NO_FACE":
            return jsonify({
                "status": "RETRY",
                "confidence": 0,
                "reason": "NO_FACE_DETECTED"
            }), 400

        if status1 == "MULTIPLE_FACES" or status2 == "MULTIPLE_FACES":
            return jsonify({
                "status": "REJECT",
                "confidence": 0,
                "reason": "MULTIPLE_FACES_DETECTED"
            }), 400

        if emb1 is None or emb2 is None:
            return jsonify({
                "status": "ERROR",
                "confidence": 0,
                "reason": "EMBEDDING_FAILED"
            }), 500


        score = calculate_similarity(emb1, emb2)
        decision = make_decision(score)

        # Log the decision
        log_event(f"Decision: {decision}")

        return jsonify(decision)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500