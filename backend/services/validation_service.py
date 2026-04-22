import numpy as np


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