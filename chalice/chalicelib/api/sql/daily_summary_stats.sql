-- Daily aggregated
DROP TABLE IF EXISTS public._daily_summary_stats;
CREATE TABLE public._daily_summary_stats AS
SELECT
    audit_date,
    SUM(resources) AS total_resources,
    SUM(failed) AS total_failures,
    AVG(resources) AS avg_resources_per_account,
    AVG(failed) AS avg_fails_per_account,
    AVG(ratio) AS avg_percent_fails_per_account,
    COUNT(DISTINCT account_id) AS accounts_audited,
    CAST(COUNT(account_id) AS FLOAT)/80 AS percent_accounts_audited
FROM public._daily_account_stats
GROUP BY audit_date
ORDER BY audit_date DESC;

CREATE INDEX daily_summary_stats__audit_date ON public._daily_summary_stats (audit_date);

