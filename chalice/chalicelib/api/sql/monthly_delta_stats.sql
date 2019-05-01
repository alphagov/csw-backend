-- Monthly delta
DROP TABLE IF EXISTS public._monthly_delta_stats;
CREATE TABLE public._monthly_delta_stats AS
SELECT
    tm.audit_year,
    tm.audit_month,
    tm.total_resources - lm.total_resources AS resources_delta,
    tm.total_failures - lm.total_failures AS failures_delta,
    tm.avg_resources_per_account - lm.avg_resources_per_account AS avg_resources_delta,
    tm.avg_fails_per_account - lm.avg_fails_per_account AS avg_fails_delta,
    tm.avg_percent_fails_per_account - lm.avg_percent_fails_per_account AS avg_percent_fails_delta,
    tm.accounts_audited - lm.accounts_audited as accounts_audited_delta
FROM public._monthly_summary_stats AS tm
INNER JOIN public._monthly_summary_stats AS lm
ON ((tm.audit_year*12)+(tm.audit_month)) = ((lm.audit_year*12)+(lm.audit_month)+1);

CREATE INDEX monthly_delta_stats__audit_year ON public._monthly_delta_stats (audit_year);
CREATE INDEX monthly_delta_stats__audit_month ON public._monthly_delta_stats (audit_month);


