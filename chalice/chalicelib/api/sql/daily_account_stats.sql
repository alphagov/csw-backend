-- Daily stats per account
DROP TABLE IF EXISTS public._daily_account_stats;

CREATE TABLE public._daily_account_stats AS
SELECT
    DATE(aud.audit_date) AS audit_date,
    sub.account_id,
    aud.id,
    SUM(achk.resources) AS resources,
    SUM(achk.failed) AS failed,
    CAST(SUM(achk.failed) AS FLOAT)/SUM(achk.resources) AS ratio
FROM public._daily_account_audits AS aud
INNER JOIN public.account_subscription AS sub
ON sub.id = aud.account_subscription_id
LEFT JOIN public.audit_criterion AS achk
ON aud.id = achk.account_audit_id
GROUP BY DATE(aud.audit_date),sub.account_id,aud.id
HAVING aud.audit_date IS NOT NULL AND SUM(achk.resources) > 0
ORDER BY sub.account_id, DATE(aud.audit_date) DESC;

CREATE INDEX daily_account_stats__account_id ON public._daily_account_stats (account_id);
CREATE INDEX daily_account_stats__audit_date ON public._daily_account_stats (audit_date);

