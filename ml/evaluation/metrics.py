def evaluate_metrics(genuine_scores, imposter_scores, accept_threshold, reject_threshold):
    false_accepts = 0
    false_rejects = 0
    correct = 0

    # Genuine → should be ACCEPT
    for score in genuine_scores:
        if score >= accept_threshold:
            correct += 1
        elif score <= reject_threshold:
            false_rejects += 1
        else:
            # PENDING treated as incorrect (conservative)
            false_rejects += 1

    # Imposter → should be REJECT
    for score in imposter_scores:
        if score <= reject_threshold:
            correct += 1
        elif score >= accept_threshold:
            false_accepts += 1
        else:
            # PENDING treated as incorrect
            false_accepts += 1

    total = len(genuine_scores) + len(imposter_scores)

    FAR = false_accepts / len(imposter_scores) if imposter_scores else 0
    FRR = false_rejects / len(genuine_scores) if genuine_scores else 0
    accuracy = correct / total if total else 0

    return {
        "FAR": FAR,
        "FRR": FRR,
        "accuracy": accuracy
    }