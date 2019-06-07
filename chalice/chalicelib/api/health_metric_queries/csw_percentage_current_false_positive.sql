-- What percentage of identified misconfigurations are
-- labelled as false positives / not to be actioned?
-- COUNT(*) returns all audit resources from the latest audits
-- SUM(CASE( returns only those with a status_id = 4 (recorded as exceptions)
SELECT
  CAST(
    SUM(
      CASE
      WHEN comp.status_id = 4
      THEN 1
      ELSE 0
      END
    ) AS FLOAT
  )/COUNT(*) AS metric_data
FROM public.account_latest_audit AS latest
LEFT JOIN public.audit_resource AS res
ON latest.account_audit_id = res.account_audit_id
LEFT JOIN public.resource_compliance AS comp
ON res.id = comp.audit_resource_id;