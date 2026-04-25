from flask import Blueprint, request, jsonify
import qrcode
import base64
from io import BytesIO
from backend.services.db_service import get_user_by_student_id

qr_bp = Blueprint("qr", __name__)


@qr_bp.route("/generate-qr", methods=["GET"])
def generate_qr():
    try:
        student_id = request.args.get("student_id")

        if not student_id:
            return jsonify({"error": "student_id is required"}), 400

        user = get_user_by_student_id(student_id)

        if not user or not user.get("qr_token"):
            return jsonify({"error": "User not found"}), 404

        qr_token = user["qr_token"]

        # Generate QR
        qr = qrcode.make(qr_token)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "student_id": student_id,
            "qr_token": qr_token,
            "qr_image_base64": qr_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@qr_bp.route("/validate-qr", methods=["POST"])
def validate_qr():
    try:
        data = request.get_json()
        qr_token = data.get("qr_token")

        if not qr_token:
            return jsonify({
                "status": "INVALID",
                "message": "qr_token required"
            }), 400

        # -------- FETCH USER VIA QR --------
        import psycopg2
        import os
        from dotenv import load_dotenv

        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL")

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT student_id, name
            FROM users
            WHERE qr_token = %s
        """, (qr_token,))

        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            return jsonify({
                "status": "INVALID",
                "message": "QR not recognized"
            }), 400

        student_id, name = row

        return jsonify({
            "status": "VALID",
            "student_id": student_id,
            "name": name
        })

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500