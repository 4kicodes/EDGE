from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import psycopg

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("DB URL Loaded:", DATABASE_URL is not None)

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Backend is running"})

@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "API working"})

@app.route("/api/db-test")

def db_test():
    try:
        conn = psycopg.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        conn.close()

        return jsonify({"db_status": "connected", "result": result[0]})
    except Exception as e:
        return jsonify({"db_status": "error", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)