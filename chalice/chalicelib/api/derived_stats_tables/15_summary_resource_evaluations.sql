DROP TABLE IF EXISTS public._summary_resource_evaluations;

CREATE TABLE public._summary_resource_evaluations AS
SELECT
  agg.resource_persistent_id,
  agg.criterion_id,
  agg.passed_audits,
  agg.failed_audits,
  agg.audited_days,
  agg.last_resource_id,
  agg.days_passed,
  agg.days_failed,
  last_ev.status_id AS current_status_id,
  (last_ev.account_audit_id = latest_audit.id) AS is_latest,
  latest_audit.finished as latest_completed
FROM (
  SELECT
    ev.resource_persistent_id,
    ev.criterion_id,
    SUM(passed_audits) AS passed_audits,
    SUM(failed_audits) AS failed_audits,
    SUM(audited_days) AS audited_days,
    CAST(SUM(ratio_audits_passed * audited_days) AS INTEGER) AS days_passed,
    CAST(SUM((1-ratio_audits_passed) * audited_days) AS INTEGER) AS days_failed,
    MAX(ev.last_resource_id) AS last_resource_id
  FROM public._monthly_resource_evaluations AS ev
  GROUP BY
    ev.resource_persistent_id,
    ev.criterion_id
) AS agg
INNER JOIN _resource_evaluations AS last_ev
ON agg.last_resource_id = last_ev.audit_resource_id
INNER JOIN account_audit AS last_ev_audit
ON last_ev.account_audit_id = last_ev_audit.id
INNER JOIN account_latest_audit AS latest
ON last_ev_audit.account_subscription_id = latest.account_subscription_id
INNER JOIN account_audit AS latest_audit
ON latest.account_audit_id = latest_audit.id;

CREATE INDEX summary_resource_evaluations__resource_persistent_id ON public._summary_resource_evaluations (resource_persistent_id);
CREATE INDEX summary_resource_evaluations__criterion_id ON public._summary_resource_evaluations (criterion_id);
