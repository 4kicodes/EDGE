from flask import Blueprint, request, jsonify
from backend.utils.image_utils import base64_to_image
from backend.services.face_service import get_face_embedding
from backend.services.db_service import insert_user
import uuid

register_bp = Blueprint("register", __name__)


@register_bp.route("/register-user", methods=["POST"])
def register_user():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Invalid or missing JSON payload"
            }), 400

        # -------- SYSTEM GENERATED ID --------
        student_id = str(uuid.uuid4())

        name = data.get("name")
        images = data.get("images")

        # -------- VALIDATION --------
        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Invalid name"
            }), 400

        if not isinstance(images, list):
            return jsonify({
                "error": "images must be a list"
            }), 400

        if len(images) < 5:
            return jsonify({
                "error": "At least 5 images are required for registration"
            }), 400

        if len(images) > 10:
            return jsonify({
                "error": "Maximum 10 images allowed"
            }), 400

        name = name.strip()

        # -------- EXTRACT EMBEDDINGS --------
        embeddings = []
        failed_images = 0

        for img_base64 in images:
            try:
                img = base64_to_image(img_base64)

                if img is None:
                    failed_images += 1
                    continue

                status, emb = get_face_embedding(img)

                if status != "OK" or emb is None:
                    failed_images += 1
                    continue

                embeddings.append(emb.tolist())

            except Exception:
                failed_images += 1
                continue

        # -------- QUALITY CHECK --------
        total_images = len(images)
        valid_embeddings = len(embeddings)
        failure_ratio = failed_images / total_images

        if valid_embeddings < 3:
            return jsonify({
                "error": "At least 3 valid face embeddings required",
                "valid_embeddings": valid_embeddings,
                "failed_images": failed_images
            }), 400

        if failure_ratio > 0.5:
            return jsonify({
                "error": "Too many invalid images. Please recapture with clear face visibility.",
                "valid_embeddings": valid_embeddings,
                "failed_images": failed_images,
                "failure_ratio": round(failure_ratio, 2)
            }), 400

        # -------- QR TOKEN (STATIC) --------
        qr_token = str(uuid.uuid4())

        # -------- STORE USER --------
        success, msg = insert_user(
            student_id=student_id,
            name=name,
            embeddings=embeddings,
            qr_token=qr_token
        )

        if not success:
            return jsonify({
                "success": False,
                "message": msg
            }), 500

        # -------- RESPONSE --------
        return jsonify({
            "success": True,
            "message": msg,
            "student_id": student_id,
            "qr_token": qr_token,
            "embeddings_stored": len(embeddings)
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500