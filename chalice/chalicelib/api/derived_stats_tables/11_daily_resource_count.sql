DROP TABLE IF EXISTS public._daily_resource_count;

CREATE TABLE public._daily_resource_count AS
SELECT
  DATE(a.date_completed) AS audit_date,
  COUNT(DISTINCT a.account_subscription_id) AS audited_accounts,
  SUM(CASE WHEN status_id = 3 THEN 1 ELSE 0 END) AS failed,
  SUM(CASE WHEN status_id = 2 THEN 1 ELSE 0 END) AS passed,
  SUM(CASE WHEN status_id = 4 THEN 1 ELSE 0 END) AS ignored
FROM (
    SELECT *
    FROM public.audit_resource AS resources
    WHERE DATE_PART('day', CURRENT_TIMESTAMP - resources.date_evaluated) < 95
) AS r
INNER JOIN public.resource_compliance AS rc
ON rc.audit_resource_id = r.id
INNER JOIN public.account_audit AS a
ON r.account_audit_id = a.id
INNER JOIN public.criterion AS c
ON r.criterion_id = c.id
WHERE a.date_completed IS NOT NULL
AND c.severity = 1
GROUP BY DATE(a.date_completed)
ORDER BY DATE(a.date_completed);