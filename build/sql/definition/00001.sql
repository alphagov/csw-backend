CREATE TABLE IF NOT EXISTS public._metadata_version(
    type VARCHAR(10) NOT NULL PRIMARY KEY,
    version INT DEFAULT 0
);

INSERT INTO public._metadata_version (type, version)
VALUES
('definition', 0),
('population', 0)
ON CONFLICT DO NOTHING;