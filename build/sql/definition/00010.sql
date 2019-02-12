CREATE TABLE IF NOT EXISTS audit_profile(
    id SERIAL PRIMARY KEY,
    profile_name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS audit_profile_criterion(
    id SERIAL PRIMARY KEY,
    audit_profile_id INT NOT NULL,
    criterion_id INT NOT NULL,
    display BOOLEAN DEFAULT TRUE,
    CONSTRAINT "audit_profile_criterion_audit_profile_id_fkey" FOREIGN KEY (audit_profile_id)
      REFERENCES  "audit_profile" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "audit_profile_criterion_criterion_id_fkey" FOREIGN KEY (criterion_id)
      REFERENCES "criterion" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);