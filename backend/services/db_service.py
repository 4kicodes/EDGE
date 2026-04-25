import psycopg
import os
from dotenv import load_dotenv
from backend.utils.logger import log_event
import json
from pathlib import Path
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("DB connection error:", str(e))
        return None
    
def insert_attendance(student_id, session_id, date, status, confidence, request_id):
    retries = 2

    for attempt in range(retries + 1):
        try:
            conn = get_connection()
            if conn is None:
                raise Exception("DB_CONNECTION_FAILED")

            cur = conn.cursor()

            query = """
            INSERT INTO attendance (student_id, session_id, date, status, confidence, request_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id, session_id, date)
            DO NOTHING;
            """

            cur.execute(query, (student_id, session_id, date, status, confidence, request_id))
            conn.commit()
            conn.close()

            log_event(f"DB Write Success on attempt {attempt} | request_id={request_id}")
            return True, f"INSERT_SUCCESS (attempt {attempt})"

        except Exception as e:
            log_event(f"DB Retry Attempt {attempt} failed: {str(e)} | request_id={request_id}")

            if attempt == retries:
                log_event(f"DB Write Failed after retries | request_id={request_id} | error={str(e)}")
                return False, f"FAILED_AFTER_RETRIES: {str(e)}"
            

def add_to_local_queue(event):
    try:
        file_path = Path("edge/local_queue/pending_events.json")

        # Ensure file exists
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("[]")

        # Read existing data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Append new event
        data.append(event)

        # Write back
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        log_event(f"Event added to local queue | request_id={event.get('request_id')}")

    except Exception as e:
        log_event(f"Failed to write to local queue: {str(e)}")


def process_local_queue():
    try:
        from pathlib import Path
        import json

        file_path = Path("edge/local_queue/pending_events.json")

        if not file_path.exists():
            return

        with open(file_path, "r") as f:
            data = json.load(f)

        if not data:
            return

        remaining_events = []

        for event in data:
            success, msg = insert_attendance(
                student_id=event["student_id"],
                session_id=event["session_id"],
                date=event["date"],
                status=event["status"],
                confidence=event["confidence"],
                request_id=event["request_id"]
            )

            if success:
                log_event(f"Queued event processed | request_id={event['request_id']}")
            else:
                remaining_events.append(event)

        # Write back only failed ones
        with open(file_path, "w") as f:
            json.dump(remaining_events, f, indent=2)

    except Exception as e:
        log_event(f"Queue processing failed: {str(e)}")



def insert_user(student_id, name, embeddings, qr_token):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # -------- CHECK EXISTING USER --------
        cur.execute("""
            SELECT student_id FROM users WHERE student_id = %s
        """, (student_id,))
        existing = cur.fetchone()

        if existing:
            cur.close()
            conn.close()
            return False, "USER_ALREADY_EXISTS"

        # -------- INSERT NEW USER --------
        cur.execute("""
            INSERT INTO users (student_id, name, embedding, qr_token)
            VALUES (%s, %s, %s, %s)
        """, (student_id, name, json.dumps(embeddings), qr_token))

        conn.commit()
        cur.close()
        conn.close()

        return True, "USER_INSERTED"

    except Exception as e:
        return False, str(e)
    

def get_user_by_student_id(student_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT student_id, name, embedding, qr_token
            FROM users
            WHERE student_id = %s
        """, (student_id,))

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            return {
                "student_id": row[0],
                "name": row[1],
                "embedding": row[2],  # REQUIRED for verify flow
                "qr_token": row[3]
            }

        return None

    except Exception as e:
        print("Fetch user error:", str(e))
        return None