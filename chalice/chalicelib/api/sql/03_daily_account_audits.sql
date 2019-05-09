-- Most recent account audit per day
DROP TABLE IF EXISTS public._daily_account_audits;

CREATE TABLE public._daily_account_audits AS
SELECT
    aud.account_subscription_id,
    DATE(aud.date_completed) AS audit_date,
    MAX(aud.id) AS id
FROM public.account_audit AS aud
GROUP BY DATE(aud.date_completed),aud.account_subscription_id
HAVING DATE(aud.date_completed) IS NOT NULL
ORDER BY aud.account_subscription_id,DATE(aud.date_completed) DESC;

CREATE INDEX daily_account_audits__account_subscription_id ON public._daily_account_audits (account_subscription_id);
CREATE INDEX daily_account_audits__audit_date ON public._daily_account_audits (audit_date);
CREATE INDEX daily_account_audits__id ON public._daily_account_audits (id);

