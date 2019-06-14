-- Current aggregated
DROP TABLE IF EXISTS public._current_summary_stats;
CREATE TABLE public._current_summary_stats AS
SELECT
  summary.total_resources,
  summary.total_failures,
  summary.avg_resources_per_account,
  summary.avg_fails_per_account,
  summary.avg_percent_fails_per_account,
  summary.accounts_audited,
  CAST(summary.accounts_audited AS FLOAT)/(coverage.accounts - coverage.suspended) AS percent_accounts_audited
FROM (
  SELECT
    SUM(acc.resources) AS total_resources,
    SUM(acc.failed) AS total_failures,
    AVG(acc.resources) AS avg_resources_per_account,
    AVG(acc.failed) AS avg_fails_per_account,
    AVG(acc.ratio) AS avg_percent_fails_per_account,
    COUNT(acc.account_id) AS accounts_audited
  FROM public._current_account_stats AS acc
) AS summary
JOIN public._current_coverage_stats AS coverage
ON 1 = 1;


