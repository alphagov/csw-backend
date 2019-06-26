DROP TABLE IF EXISTS public._monthly_resource_evaluations;

CREATE TABLE public._monthly_resource_evaluations AS
SELECT
  ev.id as resource_persistent_id,
  ev.criterion_id,
  DATE_PART('YEAR', aud.date_started) AS audit_year,
  DATE_PART('MONTH', aud.date_started) AS audit_month,
  MIN(ev.audit_resource_id) AS first_resource_id,
  MAX(ev.audit_resource_id) AS last_resource_id,
  SUM(CASE WHEN ev.status_id IN(2,4) THEN 1 ELSE 0 END) AS passed_audits,
  SUM(CASE WHEN ev.status_id = 3 THEN 1 ELSE 0 END) AS failed_audits,
  COUNT(DISTINCT DATE_PART('DAY', aud.date_started)) AS audited_days,
  CAST(SUM(CASE WHEN ev.status_id IN (2,4) THEN 1 ELSE 0 END) AS FLOAT)/COUNT(*) AS ratio_audits_passed
FROM public._resource_evaluations AS ev
INNER JOIN public.account_audit AS aud
ON aud.id = ev.account_audit_id
GROUP BY
  ev.id,
  ev.criterion_id,
  DATE_PART('YEAR', aud.date_started),
  DATE_PART('MONTH', aud.date_started);

CREATE INDEX monthly_resource_evaluations__resource_persistent_id ON public._monthly_resource_evaluations (resource_persistent_id);
CREATE INDEX monthly_resource_evaluations__criterion_id ON public._monthly_resource_evaluations (criterion_id);
CREATE INDEX monthly_resource_evaluations__first_resource_id ON public._monthly_resource_evaluations (first_resource_id);
CREATE INDEX monthly_resource_evaluations__last_resource_id ON public._monthly_resource_evaluations (last_resource_id);
CREATE INDEX monthly_resource_evaluations__audit_year ON public._monthly_resource_evaluations (audit_year);
CREATE INDEX monthly_resource_evaluations__audit_month ON public._monthly_resource_evaluations (audit_month);
