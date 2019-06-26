-- What percentage of audited resources have been actioned?
-- Actioned resources are those which either either no longer present
--   or which have changed from failed to passed
--   because we've aggregated to the criterion_id and resource_persistent_id
--   an actioned resource is anything which has had a previous failed audit
-- This stat does not account for resources which are temporarily fixed
--   multiple times.
SELECT
CAST(SUM(
CASE WHEN
(
  failed_audits > 0
)
AND
(
  (
    is_latest AND current_status_id IN (2,4)
  ) OR (
    current_status_id = 3 AND (NOT is_latest) AND latest_completed
  )
) THEN 1 ELSE 0 END
) AS FLOAT)/COUNT(*) AS actioned
FROM _summary_resource_evaluations;