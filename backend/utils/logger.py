import datetime


def log_event(message):
    try:
        timestamp = datetime.datetime.now().isoformat()

        log_line = f"{timestamp} | {message}\n"

        with open("logs/app.log", "a") as f:
            f.write(log_line)

    except Exception as e:
        print("Logging error:", str(e))


def log_metrics(message):
    from datetime import datetime
    import os

    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/aki/EDGE/logs"))
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "metrics.log")

    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {message}\n")


def log_decision_count(decision):
    import os
    import json

    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs/decision_counts.json"))

    # Initialize file if not exists
    if not os.path.exists(file_path):
        counts = {"ACCEPT": 0, "REJECT": 0, "PENDING": 0, "RETRY": 0}
    else:
        with open(file_path, "r") as f:
            counts = json.load(f)

    # Increment
    if decision in counts:
        counts[decision] += 1

    # Save back
    with open(file_path, "w") as f:
        json.dump(counts, f, indent=2)