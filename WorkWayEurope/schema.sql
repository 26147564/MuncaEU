PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS applicant (
    applicant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    phone TEXT NOT NULL,
    residence_country TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_application (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    message TEXT NOT NULL,
    consent_given INTEGER NOT NULL CHECK (consent_given IN (0, 1)),
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicant(applicant_id)
);

CREATE INDEX IF NOT EXISTS idx_job_application_applicant
ON job_application(applicant_id);

-- View applications in the SQLite terminal:
-- SELECT a.full_name, a.email, a.phone, j.job_title, j.message, j.submitted_at
-- FROM job_application AS j
-- JOIN applicant AS a ON a.applicant_id = j.applicant_id
-- ORDER BY j.submitted_at DESC;
