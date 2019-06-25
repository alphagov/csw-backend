-- What percentage of audited resources have been actioned?
-- Passed resources are one of:
--   The current status is passed or excepted and is from the latest audit
--   The current status is passed but is not from the latest audit and the
--   latest audit completed (the resource is no longer there)
SELECT
  AVG(days_failed) as days_failed
FROM _summary_resource_evaluations
WHERE (
  is_latest AND current_status_id IN (2,4)
) OR (
  current_status_id = 3 AND (NOT is_latest) AND latest_completed
);