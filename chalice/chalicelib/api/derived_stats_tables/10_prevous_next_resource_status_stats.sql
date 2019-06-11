DROP TABLE IF EXISTS public._previous_next_resource_status_stats;

CREATE TABLE public._previous_next_resource_status_stats AS
SELECT
	prev_res.resource_persistent_id,
	prev_res.criterion_id,
	seq.prev_id AS prev_audit_id,
	prev_aud.date_started AS prev_date,
	prev_aud.finished AS prev_audit_finished,
	prev_res.id AS prev_audit_resource_id,
	prev_comp.status_id AS prev_status_id,
	seq.next_id AS next_audit_id,
	next_aud.date_started AS next_date,
	next_aud.finished AS next_audit_finished,
	next_res.id AS next_audit_resource_id,
	next_comp.status_id AS next_status_id
FROM public._previous_next_audit_id_stats AS seq
INNER JOIN public.account_audit AS prev_aud
ON seq.prev_id = prev_aud.id
INNER JOIN public.account_audit AS next_aud
ON seq.next_id = next_aud.id
INNER JOIN public.audit_resource AS prev_res
ON seq.prev_id = prev_res.account_audit_id
INNER JOIN public.resource_compliance AS prev_comp
ON prev_res.id = prev_comp.audit_resource_id
LEFT JOIN public.audit_resource AS next_res
ON seq.next_id = next_res.account_audit_id
AND prev_res.resource_persistent_id = next_res.resource_persistent_id
AND prev_res.criterion_id = next_res.criterion_id
LEFT JOIN public.resource_compliance AS next_comp
ON next_res.id = next_comp.audit_resource_id
WHERE prev_res.resource_persistent_id IS NOT NULL;

CREATE INDEX previous_next_resource_status_stats__resource_persistent_id ON public._previous_next_resource_status_stats (resource_persistent_id);
CREATE INDEX previous_next_resource_status_stats__criterion_id ON public._previous_next_resource_status_stats (criterion_id);
CREATE INDEX previous_next_resource_status_stats__prev_audit_id ON public._previous_next_resource_status_stats (prev_audit_id);
CREATE INDEX previous_next_resource_status_stats__next_audit_id ON public._previous_next_resource_status_stats (next_audit_id);
CREATE INDEX previous_next_resource_status_stats__prev_audit_resource_id ON public._previous_next_resource_status_stats (prev_audit_resource_id);
CREATE INDEX previous_next_resource_status_stats__next_audit_resource_id ON public._previous_next_resource_status_stats (next_audit_resource_id);
