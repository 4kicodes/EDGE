import datetime


def log_event(message):
    try:
        timestamp = datetime.datetime.now().isoformat()

        log_line = f"{timestamp} | {message}\n"

        with open("logs/app.log", "a") as f:
            f.write(log_line)

    except Exception as e:
        print("Logging error:", str(e))