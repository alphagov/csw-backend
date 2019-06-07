-- What percentage of active accounts have a complete audit less than 24 hours old?
-- Filter on account_subscription active=True
-- Filter on either audits from last 24 hours or no audit for account
-- COUNT(*) returns all active accounts
-- SUM(CASE( returns only those with a recent audit
SELECT
  CAST(
    SUM(
      CASE
        WHEN aa.date_completed IS NOT NULL THEN 1
        ELSE 0
      END
    )
    AS FLOAT
  )/COUNT(*) as metric_data
FROM public.account_subscription AS sub
LEFT JOIN public.account_audit AS aa
ON sub.id = aa.account_subscription_id
WHERE
  sub.active
  AND
  (
    (age(NOW(), aa.date_started) < INTERVAL '24 hours')
    OR
    aa.date_started IS NULL
  )