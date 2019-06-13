DROP TABLE IF EXISTS public._previous_next_resource_stats;

CREATE TABLE public._previous_next_resource_stats AS
SELECT
	prev_res.resource_persistent_id,
	prev_res.criterion_id,
	seq.prev_id AS prev_audit_id,
	seq.prev_date,
	seq.prev_finished,
	prev_res.id AS prev_audit_resource_id,
	seq.next_id AS next_audit_id,
	seq.next_date,
	seq.next_finished,
	next_res.id AS next_audit_resource_id
FROM public._previous_next_audit_id_stats AS seq
INNER JOIN public.audit_resource AS prev_res
ON seq.prev_id = prev_res.account_audit_id
LEFT JOIN public.audit_resource AS next_res
ON seq.next_id = next_res.account_audit_id
AND prev_res.resource_persistent_id = next_res.resource_persistent_id
AND prev_res.criterion_id = next_res.criterion_id
WHERE prev_res.resource_persistent_id IS NOT NULL;

CREATE INDEX previous_next_resource_stats__resource_persistent_id ON public._previous_next_resource_stats (resource_persistent_id);
CREATE INDEX previous_next_resource_stats__criterion_id ON public._previous_next_resource_stats (criterion_id);
CREATE INDEX previous_next_resource_stats__prev_audit_id ON public._previous_next_resource_stats (prev_audit_id);
CREATE INDEX previous_next_resource_stats__next_audit_id ON public._previous_next_resource_stats (next_audit_id);
CREATE INDEX previous_next_resource_stats__prev_audit_resource_id ON public._previous_next_resource_stats (prev_audit_resource_id);
CREATE INDEX previous_next_resource_stats__next_audit_resource_id ON public._previous_next_resource_stats (next_audit_resource_id);
