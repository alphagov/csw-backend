DROP TABLE IF EXISTS _resource_persistent_ids;

CREATE TABLE _resource_persistent_ids AS
SELECT
row_number() OVER () AS id,
ids.resource_persistent_id
FROM (
    SELECT
    DISTINCT(res.resource_persistent_id) AS resource_persistent_id
    FROM public.audit_resource AS res
    WHERE res.resource_persistent_id IS NOT NULL
) AS ids;

CREATE INDEX resource_persistent_ids__id ON public._resource_persistent_ids (id);
CREATE INDEX resource_persistent_ids__resource_persistent_id ON public._resource_persistent_ids (resource_persistent_id);