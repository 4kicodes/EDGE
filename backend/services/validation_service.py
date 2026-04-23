import numpy as np
from backend.config.settings import ACCEPT_THRESHOLD, PENDING_THRESHOLD


def calculate_similarity(emb1, emb2):
    try:
        # Normalize vectors
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)

        # Cosine similarity
        similarity = np.dot(emb1, emb2)

        return float(similarity)
    except Exception as e:
        print("Similarity error:", str(e))
        return None


def make_decision(similarity_score):
    try:
        # High confidence match
        if similarity_score >= ACCEPT_THRESHOLD:
            return {
                "status": "ACCEPT",
                "confidence": similarity_score,
                "reason": "FACE_MATCH_HIGH",
            }

        # Medium confidence (uncertain)
        elif similarity_score >= PENDING_THRESHOLD:
            return {
                "status": "PENDING",
                "confidence": similarity_score,
                "reason": "FACE_MATCH_UNCERTAIN",
            }

        # Low confidence → reject
        else:
            return {
                "status": "REJECT",
                "confidence": similarity_score,
                "reason": "FACE_MISMATCH",
            }

    except Exception as e:
        print("Decision error:", str(e))
        return {
            "status": "ERROR",
            "confidence": 0,
            "reason": "DECISION_FAILED",
        }