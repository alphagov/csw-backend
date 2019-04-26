
-- Current
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
GROUP BY DATE(aud.date_completed),sub.account_id,aud.id
HAVING DATE(aud.date_completed) IS NOT NULL AND SUM(achk.resources) > 0;

CREATE INDEX current_account_stats__audit_date_index ON public._current_account_stats (audit_date);
CREATE INDEX current_account_stats__account_id_index ON public._current_account_stats (account_id);
CREATE INDEX current_account_stats__id_index ON public._current_account_stats (id);

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


