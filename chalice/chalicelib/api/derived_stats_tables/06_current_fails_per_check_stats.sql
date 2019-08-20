-- Current account stats
DROP TABLE IF EXISTS public._current_fails_per_check_stats;

CREATE TABLE public._current_fails_per_check_stats AS
SELECT
  team.severity,
  team.criterion_id,
  SUM(team.issues) AS issues
FROM public._current_fails_per_team_check_stats AS team
GROUP BY
  team.criterion_id,
  team.severity
ORDER BY
  team.severity,
  team.criterion_id;