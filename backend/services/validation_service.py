import numpy as np
from backend.config.settings import ACCEPT_THRESHOLD, REJECT_THRESHOLD


def calculate_similarity(emb1, emb2):
    try:
        if emb1 is None or emb2 is None:
            return None

        emb1 = np.array(emb1, dtype=np.float32)
        emb2 = np.array(emb2, dtype=np.float32)

        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        # Prevent division by zero
        if norm1 == 0 or norm2 == 0:
            return None

        emb1 = emb1 / norm1
        emb2 = emb2 / norm2

        similarity = np.dot(emb1, emb2)

        return float(similarity)

    except Exception as e:
        print("Similarity error:", str(e))
        return None


def make_decision(score):
    if score >= 0.75:
        return {
            "status": "ACCEPT",
            "confidence": float(score)
        }

    elif score >= 0.6:
        return {
            "status": "PENDING",
            "confidence": float(score)
        }

    else:
        return {
            "status": "REJECT",
            "confidence": float(score)
        }