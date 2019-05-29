-- TODO THIS NEEDS MUCHO TESTING
-- Delete all records that violate the unique constraint
DELETE FROM public.audit_criterion WHERE id NOT IN
(
  SELECT MIN(id)
  FROM public.audit_criterion
  GROUP BY account_audit_id, criterion_id
);

-- Correct stats for past audits where duplicates have been removed
UPDATE public.account_audit as audit
SET
  criteria_processed = source.criteria_processed,
  criteria_passed = source.criteria_passed,
  criteria_failed = source.criteria_failed,
  issues_found = source.issues_found
FROM (
  SELECT
    aud.id,
    COUNT(DISTINCT chk.id) AS active_criteria,
    SUM(CASE WHEN chk.processed THEN 1 ELSE 0 END) AS criteria_processed,
    SUM(CASE WHEN chk.failed = 0 THEN 1 ELSE 0 END) AS criteria_passed,
    SUM(CASE WHEN chk.failed > 0 THEN 1 ELSE 0 END) AS criteria_failed,
    SUM(chk.failed) AS issues_found
  FROM public.account_audit AS aud
  INNER JOIN public.audit_criterion AS chk
  ON aud.id = chk.account_audit_id
  GROUP BY aud.id

) AS source
WHERE audit.id = source.id;

-- Create a unique constraint so that the same check cannot be recorded twice as part of the same audit
ALTER TABLE public.audit_criterion
ADD CONSTRAINT audit_criterion_account_audit_id_and_criterion_id UNIQUE (account_audit_id, criterion_id);