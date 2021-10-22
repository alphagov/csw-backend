DROP TABLE IF EXISTS public._recent_resources;


CREATE TABLE public._recent_resources AS
SELECT r.*
    FROM public._recent_audits AS a
    INNER JOIN public.audit_resource AS r
    ON r.account_audit_id = a.id;

