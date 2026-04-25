from flask import Blueprint, request, jsonify
from backend.utils.image_utils import base64_to_image
from backend.services.face_service import get_face_embedding
from backend.services.validation_service import calculate_similarity, make_decision
from backend.services.db_service import (
    insert_attendance,
    add_to_local_queue,
    process_local_queue,
    get_user_by_student_id
)
from backend.utils.logger import log_event, log_metrics, log_decision_count

import datetime
import uuid
import time
import json
import psycopg2
import os
import numpy as np
from dotenv import load_dotenv

verify_user_bp = Blueprint("verify_user", __name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# -------- HELPER: QR → student_id --------
def get_student_id_from_qr(qr_token):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT student_id FROM users WHERE qr_token = %s
        """, (qr_token,))

        row = cur.fetchone()

        cur.close()
        conn.close()

        return row[0] if row else None

    except Exception:
        return None


# -------- MAIN API --------
@verify_user_bp.route("/verify-user", methods=["POST"])
def verify_user():
    try:
        start_time = time.time()

        # Process retry queue
        process_local_queue()

        # -------- SAFE INPUT --------
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "RETRY",
                "reason": "NO_JSON_PAYLOAD"
            }), 400

        qr_token = data.get("qr_token")
        image_base64 = data.get("image")

        if not qr_token or not image_base64:
            return jsonify({
                "status": "RETRY",
                "reason": "INVALID_INPUT"
            }), 400

        # -------- QR VALIDATION --------
        student_id = get_student_id_from_qr(qr_token)

        if not student_id:
            return jsonify({
                "status": "REJECT",
                "reason": "INVALID_QR"
            }), 400

        # -------- FETCH USER --------
        user = get_user_by_student_id(student_id)

        if not user:
            return jsonify({
                "status": "ERROR",
                "reason": "USER_NOT_FOUND"
            }), 500

        # -------- SAFE EMBEDDING LOAD --------
        embedding_data = user["embedding"]

        if isinstance(embedding_data, str):
            stored_embeddings = json.loads(embedding_data)
        else:
            stored_embeddings = embedding_data

        if not stored_embeddings or len(stored_embeddings) == 0:
            return jsonify({
                "status": "ERROR",
                "reason": "NO_EMBEDDINGS_FOUND"
            }), 500

        # -------- LIVE IMAGE --------
        img = base64_to_image(image_base64)
        status, live_emb = get_face_embedding(img)

        if status == "NO_FACE":
            return jsonify({
                "status": "RETRY",
                "reason": "NO_FACE"
            })

        if status == "MULTIPLE_FACES":
            return jsonify({
                "status": "REJECT",
                "reason": "MULTIPLE_FACES"
            })

        if live_emb is None:
            return jsonify({
                "status": "ERROR",
                "reason": "EMBEDDING_FAILED"
            }), 500

        # -------- COMPARE WITH STORED EMBEDDINGS --------
        best_score = -1

        for emb in stored_embeddings:
            emb_np = np.array(emb)
            score = calculate_similarity(live_emb, emb_np)
            best_score = max(best_score, score)

        # -------- DECISION --------
        decision = make_decision(best_score)

        request_id = str(uuid.uuid4())
        date = datetime.date.today()

        # -------- DB WRITE --------
        if decision["status"] == "ACCEPT":
            success, msg = insert_attendance(
                student_id=student_id,
                session_id="session_1",
                date=date,
                status=decision["status"],
                confidence=decision["confidence"],
                request_id=request_id
            )

            if not success:
                event = {
                    "student_id": student_id,
                    "session_id": "session_1",
                    "date": str(date),
                    "status": decision["status"],
                    "confidence": decision["confidence"],
                    "request_id": request_id
                }
                add_to_local_queue(event)

        # -------- LOGGING --------
        latency = time.time() - start_time

        log_metrics(
            f"Decision={decision['status']}, Score={best_score:.4f}, Latency={latency:.4f}s"
        )

        log_decision_count(decision["status"])

        log_event(
            f"{decision} | student_id={student_id} | request_id={request_id}"
        )

        # -------- RESPONSE --------
        return jsonify({
            "status": decision["status"],
            "confidence": decision["confidence"],
            "student_id": student_id,
            "name": user["name"]
        })

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500