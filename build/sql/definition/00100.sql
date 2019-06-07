CREATE TABLE IF NOT EXISTS _health_metrics(
    id SERIAL PRIMARY KEY,
    "name" VARCHAR(200) NOT NULL,
    "desc" TEXT NOT NULL,
    "metric_type" VARCHAR(200) NOT NULL,
    "data" FLOAT NOT NULL,
    CONSTRAINT health_metrics_name_unique UNIQUE (name)
);
