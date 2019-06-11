-- What percentage of audited resources have been actioned?
-- Subselect
--    Gets the first and last date for checked resources
--    where the state failed in both before and after audits
-- Outer query
--    Aggregates to average duration and calculates the
--    elapsed time in days
SELECT
  EXTRACT(
    HOUR FROM
    AVG(duration_failed) * INTERVAL '1 second'
  ) / 24 AS days
FROM (
  SELECT
    seq.resource_persistent_id,
    seq.criterion_id,
    MIN(seq.prev_date) AS first_failed,
    MAX(seq.next_date) AS last_failed,
    EXTRACT(
      EPOCH FROM
      MAX(seq.next_date) - MIN(seq.prev_date)
    ) AS duration_failed
  FROM public._previous_next_resource_status_stats AS seq
  WHERE seq.prev_status_id = 3
  AND seq.next_status_id = 3
  AND seq.next_audit_finished = TRUE
  GROUP BY seq.resource_persistent_id, seq.criterion_id
) AS res_fail_duration;