CREATE TABLE IF NOT EXISTS applicant (
    applicant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    residence_country VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_application (
    application_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    applicant_id BIGINT NOT NULL REFERENCES applicant(applicant_id),
    job_title VARCHAR(160) NOT NULL,
    message VARCHAR(2000) NOT NULL,
    consent_given BOOLEAN NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_application_applicant
ON job_application(applicant_id);
