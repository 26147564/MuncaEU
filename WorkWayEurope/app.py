from pathlib import Path
import re
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).parent
DATABASE = ROOT / "workway.db"
app = Flask(__name__)


def connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize_database():
    with connection() as db:
        db.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))


@app.get("/")
def home():
    return send_from_directory(ROOT, "europe-work-finder.html")


@app.post("/api/applications")
def create_application():
    data = request.get_json(silent=True) or {}
    required = ["job_title", "full_name", "email", "phone", "residence_country", "message"]
    if any(not str(data.get(field, "")).strip() for field in required):
        return jsonify(error="Completează toate câmpurile obligatorii."), 400
    if not data.get("consent"):
        return jsonify(error="Este necesar acordul pentru salvarea datelor de contact."), 400

    email = str(data["email"]).strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify(error="Adresa de e-mail nu este validă."), 400

    full_name = str(data["full_name"]).strip()
    phone = str(data["phone"]).strip()
    country = str(data["residence_country"]).strip()
    job_title = str(data["job_title"]).strip()
    message = str(data["message"]).strip()
    if len(full_name) > 120 or len(phone) > 30 or len(job_title) > 160 or len(message) > 2000:
        return jsonify(error="Unul dintre câmpuri este prea lung."), 400

    with connection() as db:
        db.execute("""
            INSERT INTO applicant (full_name, email, phone, residence_country)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                full_name=excluded.full_name,
                phone=excluded.phone,
                residence_country=excluded.residence_country
        """, (full_name, email, phone, country))
        applicant_id = db.execute(
            "SELECT applicant_id FROM applicant WHERE email = ?", (email,)
        ).fetchone()["applicant_id"]
        db.execute("""
            INSERT INTO job_application (applicant_id, job_title, message, consent_given)
            VALUES (?, ?, ?, 1)
        """, (applicant_id, job_title, message))
    return jsonify(message="Candidatura a fost salvată."), 201


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
