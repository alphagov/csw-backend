DROP TABLE IF EXISTS _resource_evaluations;

CREATE TABLE _resource_evaluations AS
SELECT
  res.audit_resource_id,
  res.account_audit_id,
  res.criterion_id,
  res.id,
  comp.status_id
FROM public._resources AS res
INNER JOIN public.resource_compliance AS comp
ON res.audit_resource_id = comp.audit_resource_id;

CREATE INDEX resource_evaluations__id ON public._resource_evaluations (id);
CREATE INDEX resource_evaluations__status_id ON public._resource_evaluations (status_id);
CREATE INDEX resource_evaluations__criterion_id ON public._resource_evaluations (criterion_id);
CREATE INDEX resource_evaluations__audit_resource_id ON public._resource_evaluations (audit_resource_id);
CREATE INDEX resource_evaluations__account_audit_id ON public._resource_evaluations (account_audit_id);