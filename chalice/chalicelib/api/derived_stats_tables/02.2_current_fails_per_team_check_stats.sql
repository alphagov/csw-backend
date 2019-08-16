-- Current account stats
DROP TABLE IF EXISTS public._current_fails_per_team_check_stats;

CREATE TABLE public._current_fails_per_team_check_stats AS
SELECT
  acc.severity,
  acc.criterion_id,
  acc.team_id,
  SUM(acc.issues) AS issues
FROM public._current_fails_per_account_check_stats AS acc
GROUP BY
  acc.criterion_id,
  acc.team_id,
  acc.severity
ORDER BY
  acc.severity,
  acc.criterion_id,
  acc.team_id;