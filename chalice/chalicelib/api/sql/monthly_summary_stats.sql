-- Monthly aggregated
DROP TABLE IF EXISTS public._monthly_summary_stats;
CREATE TABLE public._monthly_summary_stats AS
SELECT
    CAST(date_part('YEAR', audit_date) AS INTEGER) AS audit_year,
    CAST(date_part('MONTH', audit_date) AS INTEGER) AS audit_month,
    SUM(resources) AS total_resources,
    SUM(failed) AS total_failures,
    AVG(resources) AS avg_resources_per_account,
    AVG(failed) AS avg_fails_per_account,
    AVG(ratio) AS avg_percent_fails_per_account,
    COUNT(DISTINCT account_id) AS accounts_audited,
    CAST(COUNT(account_id) AS FLOAT)/80 AS percent_accounts_audited
FROM public._daily_account_stats
GROUP BY  date_part('YEAR', audit_date),date_part('MONTH', audit_date)
ORDER BY date_part('YEAR', audit_date) DESC,date_part('MONTH', audit_date) DESC;

CREATE INDEX monthly_summary_stats__audit_year ON public._monthly_summary_stats (audit_year);
CREATE INDEX monthly_summary_stats__audit_month ON public._monthly_summary_stats (audit_month);

