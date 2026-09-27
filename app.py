from pathlib import Path
import os
import re

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request, send_file

ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get("DATABASE_URL")
app = Flask(__name__)


def homepage_file():
    for filename in (
        "europe-work-finder.html",
        "europe-work-finder_v3.html",
        "europe-work-finder_v2.html",
    ):
        file = ROOT / filename
        if file.is_file():
            return file
    return None


def connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@app.get("/")
@app.get("/app.py")
def home():
    file = homepage_file()
    if file:
        return send_file(file, mimetype="text/html")
    return jsonify(
        error="Homepage HTML file is missing.",
        expected_files=["europe-work-finder.html", "europe-work-finder_v3.html"],
    ), 500


@app.get("/api/health")
def health():
    return jsonify(status="ok", homepage_found=homepage_file() is not None)


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
    if (
        len(full_name) > 120
        or len(phone) > 30
        or len(country) > 100
        or len(job_title) > 160
        or len(message) > 2000
    ):
        return jsonify(error="Unul dintre câmpuri este prea lung."), 400

    try:
        with connection() as db, db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO applicant (full_name, email, phone, residence_country)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    phone = EXCLUDED.phone,
                    residence_country = EXCLUDED.residence_country
                RETURNING applicant_id
                """,
                (full_name, email, phone, country),
            )
            applicant_id = cur.fetchone()["applicant_id"]
            cur.execute(
                """
                INSERT INTO job_application (applicant_id, job_title, message, consent_given)
                VALUES (%s, %s, %s, TRUE)
                """,
                (applicant_id, job_title, message),
            )
    except Exception:
        app.logger.exception("Could not save application")
        return jsonify(error="Candidatura nu a putut fi salvată. Încearcă din nou."), 500

    return jsonify(message="Candidatura a fost salvată."), 201


if __name__ == "__main__":
    app.run(debug=True)
