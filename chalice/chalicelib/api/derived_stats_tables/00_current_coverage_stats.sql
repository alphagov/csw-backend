DROP TABLE IF EXISTS public._current_coverage_stats;

CREATE TABLE public._current_coverage_stats AS
SELECT
  COUNT(*) AS accounts,
  SUM(CASE WHEN active THEN 1 ELSE 0 END) AS active,
  SUM(CASE WHEN auditable THEN 1 ELSE 0 END) AS auditable,
  SUM(CASE WHEN suspended THEN 1 ELSE 0 END) AS suspended,
  CAST(SUM(CASE WHEN auditable THEN 1 ELSE 0 END) AS FLOAT)/SUM(CASE WHEN active THEN 1 ELSE 0 END) AS coverage
FROM public.account_subscription;