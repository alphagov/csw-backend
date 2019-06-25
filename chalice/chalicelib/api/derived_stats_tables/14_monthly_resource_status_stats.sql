DROP TABLE IF EXISTS public._monthly_resource_status_stats;

CREATE TABLE public._monthly_resource_status_stats AS
SELECT
    pn.resource_persistent_id,
    pn.criterion_id,
    CAST(pn.audit_year AS INTEGER),
    CAST(pn.audit_month AS INTEGER),
    pn.first_resource_id,
    audf.id as first_audit_id,
    audf.date_started AS first_audit_date,
    audf.finished AS first_completed,
    evf.status_id AS first_status_id,
    pn.last_resource_id,
    audl.id as last_audit_id,
    audl.date_started AS last_audit_date,
    audl.finished AS last_completed,
    evl.status_id AS last_status_id,
    pn.ratio_audits_passed,
    pn.audited_days,
    CAST(EXTRACT(DAY FROM (audl.date_started - audf.date_started))+1 AS INTEGER) AS elapsed_days
FROM _monthly_resource_evaluations AS pn
INNER JOIN public._resource_evaluations AS evf
ON pn.first_resource_id = evf.audit_resource_id
INNER JOIN public.account_audit AS audf
ON evf.account_audit_id = audf.id
INNER JOIN public._resource_evaluations AS evl
ON pn.last_resource_id = evl.audit_resource_id
INNER JOIN public.account_audit AS audl
ON evl.account_audit_id = audl.id;

CREATE INDEX monthly_resource_status_stats__resource_persistent_id ON public._monthly_resource_status_stats (resource_persistent_id);
CREATE INDEX monthly_resource_status_stats__criterion_id ON public._monthly_resource_status_stats (criterion_id);
CREATE INDEX monthly_resource_status_stats__first_audit_id ON public._monthly_resource_status_stats (first_audit_id);
CREATE INDEX monthly_resource_status_stats__last_audit_id ON public._monthly_resource_status_stats (last_audit_id);
CREATE INDEX monthly_resource_status_stats__first_resource_id ON public._monthly_resource_status_stats (first_resource_id);
CREATE INDEX monthly_resource_status_stats__last_resource_id ON public._monthly_resource_status_stats (last_resource_id);
CREATE INDEX monthly_resource_status_stats__first_status_id ON public._monthly_resource_status_stats (first_status_id);
CREATE INDEX monthly_resource_status_stats__last_status_id ON public._monthly_resource_status_stats (last_status_id);
