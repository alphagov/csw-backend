-- Daily aggregated
DROP TABLE IF EXISTS public._daily_summary_stats;
CREATE TABLE public._daily_summary_stats AS
SELECT
  summary.audit_date,
  summary.total_resources,
  summary.total_failures,
  summary.avg_resources_per_account,
  summary.avg_fails_per_account,
  summary.avg_percent_fails_per_account,
  summary.accounts_audited,
  CAST(summary.accounts_audited AS FLOAT)/(coverage.accounts - coverage.suspended) AS percent_accounts_audited
FROM (
  SELECT
    audit_date,
    SUM(resources) AS total_resources,
    SUM(failed) AS total_failures,
    AVG(resources) AS avg_resources_per_account,
    AVG(failed) AS avg_fails_per_account,
    AVG(ratio) AS avg_percent_fails_per_account,
    COUNT(DISTINCT account_id) AS accounts_audited
  FROM public._daily_account_stats
  GROUP BY audit_date
  ORDER BY audit_date DESC
) AS summary
JOIN public._current_coverage_stats AS coverage
ON 1 = 1;

CREATE INDEX daily_summary_stats__audit_date ON public._daily_summary_stats (audit_date);

