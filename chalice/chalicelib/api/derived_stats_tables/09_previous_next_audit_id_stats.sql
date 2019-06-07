DROP TABLE IF EXISTS public._previous_next_audit_id_stats;

CREATE TABLE public._previous_next_audit_id_stats AS
SELECT
    prev_aud.account_subscription_id,
    prev_aud.id AS prev_id,
    prev_aud.date_started AS prev_date,
    prev_aud.finished AS prev_finished,
    next_aud.id AS next_id,
    next_aud.date_started AS next_date,
    next_aud.finished AS next_finished
FROM public.account_audit AS prev_aud
INNER JOIN (
    SELECT
        prev_aud.id AS prev_id,
        MIN(post_aud.id) AS next_id
    FROM public.account_audit AS prev_aud
    INNER JOIN public.account_audit AS post_aud
    ON prev_aud.account_subscription_id = post_aud.account_subscription_id
    AND prev_aud.date_started < post_aud.date_started
    GROUP BY prev_aud.id
) AS seq
ON prev_aud.id = seq.prev_id
INNER JOIN public.account_audit AS next_aud
ON seq.next_id = next_aud.id
ORDER BY prev_aud.account_subscription_id, prev_aud.id;

CREATE INDEX previous_next_audit_id_stats__account_subscription_id ON public._previous_next_audit_id_stats (account_subscription_id);
CREATE INDEX previous_next_audit_id_stats__prev_id ON public._previous_next_audit_id_stats (prev_id);
CREATE INDEX previous_next_audit_id_stats__next_id ON public._previous_next_audit_id_stats (next_id);
