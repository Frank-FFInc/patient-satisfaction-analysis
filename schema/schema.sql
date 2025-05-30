CREATE TABLE IF NOT EXISTS hospitals (
    facility_id TEXT PRIMARY KEY,
    facility_name TEXT,
    state TEXT
);

CREATE TABLE IF NOT EXISTS measures (
    hcahps_measure_id TEXT PRIMARY KEY,
    hcahps_question TEXT,
    hcahps_answer_description TEXT
);

CREATE TABLE IF NOT EXISTS ratings (
    facility_id TEXT,
    hcahps_measure_id TEXT,
    patient_survey_star_rating INTEGER,
    patient_experience_national_comparison TEXT,
    FOREIGN KEY (facility_id) REFERENCES hospitals(facility_id),
    FOREIGN KEY (hcahps_measure_id) REFERENCES measures(hcahps_measure_id)
);

CREATE INDEX IF NOT EXISTS idx_state ON hospitals(state);

CREATE INDEX IF NOT EXISTS idx_hcahps_measure_id ON ratings(hcahps_measure_id)