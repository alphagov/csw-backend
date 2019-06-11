-- What percentage of audited resources have been actioned?
-- Subselect
--    Gets resources evaluated by a given check and counts how many times their
--    state has changed from fail to pass
-- Outer query
--    Counts any resources which have been actioned at least once
--    A resource may fail one day, pass the next and then fail again the day after
SELECT
  CAST(
    SUM(
      CASE
      WHEN res_fixes > 0
      THEN 1
      ELSE 0
      END
     ) AS FLOAT
    )/COUNT(*) AS fixed_once
FROM (
  SELECT
    seq.resource_persistent_id,
    seq.criterion_id,
    COUNT(*) AS res_entries,
    SUM(
      CASE
      WHEN (
        seq.prev_status_id = 3
        AND (
          (seq.next_audit_finished = TRUE AND seq.next_audit_resource_id IS NULL)
          OR
          (seq.next_status_id IN(2,4))
        )
      )
      THEN 1
      ELSE 0
      END
    ) AS res_fixes
  FROM public._previous_next_resource_status_stats AS seq
  GROUP BY seq.resource_persistent_id, seq.criterion_id
) AS res_fixes;