-- Current aggregated
DROP TABLE IF EXISTS public._current_summary_stats;
CREATE TABLE public._current_summary_stats AS
SELECT
    SUM(resources) AS total_resources,
    SUM(failed) AS total_failures,
    AVG(resources) AS avg_resources_per_account,
    AVG(failed) AS avg_fails_per_account,
    AVG(ratio) AS avg_percent_fails_per_account,
    COUNT(account_id) AS accounts_audited,
    CAST(COUNT(account_id) AS FLOAT)/80 AS percent_accounts_audited
FROM public._current_account_stats;


