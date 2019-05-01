-- Daily delta
DROP TABLE IF EXISTS public._daily_delta_stats;
CREATE TABLE public._daily_delta_stats AS
SELECT
    today.audit_date AS audit_date,
    today.total_resources - yesterday.total_resources AS resources_delta,
    today.total_failures - yesterday.total_failures AS failures_delta,
    today.avg_resources_per_account - yesterday.avg_resources_per_account AS avg_resources_delta,
    today.avg_fails_per_account - yesterday.avg_fails_per_account AS avg_fails_delta,
    today.avg_percent_fails_per_account - yesterday.avg_percent_fails_per_account AS avg_percent_fails_delta,
    today.accounts_audited - yesterday.accounts_audited as accounts_audited_delta
FROM public._daily_summary_stats AS today
INNER JOIN public._daily_summary_stats AS yesterday
ON today.audit_date = (yesterday.audit_date + 1);

CREATE INDEX daily_delta_stats__audit_date ON public._daily_delta_stats (audit_date);


