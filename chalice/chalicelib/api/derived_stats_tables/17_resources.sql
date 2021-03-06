DROP TABLE IF EXISTS _resources;

CREATE TABLE _resources AS
SELECT
res.id AS audit_resource_id,
res.account_audit_id,
res.criterion_id,
ids.id
FROM public.audit_resource AS res
INNER JOIN public._resource_persistent_ids AS ids
ON res.resource_persistent_id = ids.resource_persistent_id
INNER JOIN public.criterion AS c
ON res.criterion_id = c.id
INNER JOIN public.account_audit as aud
ON aud.id = res.account_audit_id
WHERE res.resource_persistent_id IS NOT NULL
AND c.severity = 1
AND age(NOW(), aud.date_started) < INTERVAL '28 days';

CREATE INDEX resources__audit_resource_id ON public._resources (audit_resource_id);
CREATE INDEX resources__account_audit_id ON public._resources (account_audit_id);
CREATE INDEX resources__criterion_id ON public._resources (criterion_id);
CREATE INDEX resources__id ON public._resources (id);