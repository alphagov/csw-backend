-- Current account stats
DROP TABLE IF EXISTS public._current_fails_per_account_check_stats;

CREATE TABLE public._current_fails_per_account_check_stats AS
SELECT
  c.severity,
  c.id AS criterion_id,
  t.id AS team_id,
  a.account_id,
  COUNT(*) AS issues
FROM public.account_latest_audit AS ala
INNER JOIN public.account_subscription AS a
ON ala.account_subscription_id = a.id
INNER JOIN public.product_team AS t
ON a.product_team_id = t.id
INNER JOIN public.audit_resource AS ar
ON ala.account_audit_id = ar.account_audit_id
INNER JOIN public.criterion AS c
ON ar.criterion_id = c.id
INNER JOIN public.resource_compliance AS rc
ON ar.id = rc.audit_resource_id
WHERE rc.status_id = 3
GROUP BY
  t.id,
  t.team_name,
  a.account_id,
  c.id,
  c.title,
  c.severity
ORDER BY
  c.severity,
  t.team_name,
  a.account_id,
  c.title;