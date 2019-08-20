DROP TABLE IF EXISTS public._monthly_resource_count;

CREATE TABLE public._monthly_resource_count AS
SELECT
  CAST(date_part('YEAR', audit_date) AS INTEGER) AS audit_year,
  CAST(date_part('MONTH', audit_date) AS INTEGER) AS audit_month,
  AVG(audited_accounts) AS audited_accounts,
  AVG(failed) AS failed,
  AVG(passed) AS passed,
  AVG(ignored) AS ignored
FROM public._daily_resource_count AS d
GROUP BY
  CAST(date_part('YEAR', audit_date) AS INTEGER),
  CAST(date_part('MONTH', audit_date) AS INTEGER)
ORDER BY
  CAST(date_part('YEAR', audit_date) AS INTEGER),
  CAST(date_part('MONTH', audit_date) AS INTEGER);