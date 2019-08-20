-- Current account stats
DROP TABLE IF EXISTS public._current_account_stats;

CREATE TABLE public._current_account_stats AS
SELECT
    DATE(aud.date_completed) AS audit_date,
    sub.account_id,
    aud.id,
    SUM(achk.resources) AS resources,
    SUM(achk.failed) AS failed,
    CAST(SUM(achk.failed) AS FLOAT)/SUM(achk.resources) AS ratio
FROM public.account_latest_audit AS lat
INNER JOIN public.account_subscription AS sub
ON lat.account_subscription_id = sub.id
INNER JOIN public.account_audit AS aud
ON lat.account_audit_id = aud.id
LEFT JOIN public.audit_criterion AS achk
ON aud.id = achk.account_audit_id
LEFT JOIN public.criterion AS chk
ON achk.criterion_id = chk.id
GROUP BY DATE(aud.date_completed),sub.account_id,aud.id,chk.severity
HAVING DATE(aud.date_completed) IS NOT NULL
AND SUM(achk.resources) > 0
AND chk.severity = 1;

CREATE INDEX current_account_stats__audit_date_index ON public._current_account_stats (audit_date);
CREATE INDEX current_account_stats__account_id_index ON public._current_account_stats (account_id);
CREATE INDEX current_account_stats__id_index ON public._current_account_stats (id);

