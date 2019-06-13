DROP TABLE IF EXISTS public._previous_next_resource_status_stats;

CREATE TABLE public._previous_next_resource_status_stats AS
SELECT
  seq.resource_persistent_id,
	seq.criterion_id,
	seq.prev_audit_id,
	seq.prev_date,
	seq.prev_finished,
	seq.prev_audit_resource_id,
	prev_comp.status_id AS prev_status_id,
	seq.next_audit_id,
	seq.next_date,
	seq.next_finished,
	seq.next_audit_resource_id,
	next_comp.status_id AS next_status_id
FROM public._previous_next_resource_stats AS seq
INNER JOIN public.resource_compliance AS prev_comp
ON seq.prev_audit_resource_id = prev_comp.audit_resource_id
INNER JOIN public.resource_compliance AS next_comp
ON seq.next_audit_resource_id = next_comp.audit_resource_id;

CREATE INDEX previous_next_resource_status_stats__resource_persistent_id ON public._previous_next_resource_status_stats (resource_persistent_id);
CREATE INDEX previous_next_resource_status_stats__criterion_id ON public._previous_next_resource_status_stats (criterion_id);
CREATE INDEX previous_next_resource_status_stats__prev_audit_id ON public._previous_next_resource_status_stats (prev_audit_id);
CREATE INDEX previous_next_resource_status_stats__next_audit_id ON public._previous_next_resource_status_stats (next_audit_id);
CREATE INDEX previous_next_resource_status_stats__prev_audit_resource_id ON public._previous_next_resource_status_stats (prev_audit_resource_id);
CREATE INDEX previous_next_resource_status_stats__next_audit_resource_id ON public._previous_next_resource_status_stats (next_audit_resource_id);
CREATE INDEX previous_next_resource_status_stats__prev_status_id ON public._previous_next_resource_status_stats (prev_status_id);
CREATE INDEX previous_next_resource_status_stats__next_status_id ON public._previous_next_resource_status_stats (next_status_id);
