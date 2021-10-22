DROP TABLE IF EXISTS public._recent_audits;


CREATE TABLE public._recent_audits AS
SELECT *
    FROM public.account_audit AS audit
    WHERE audit.date_completed IS NOT NULL
    AND DATE_PART('day', CURRENT_TIMESTAMP - audit.date_completed) < 15;


