-- What percentage of audits have run and completed in the past 7 days?
-- Filter on account_subscription active=True
-- Filter on either audits from last 7 days
-- COUNT(*) returns all audits
-- SUM(CASE( returns only those with a completed audit
SELECT
  CAST(
    SUM(
      CASE
      WHEN aa.date_completed IS NOT NULL
      THEN 1
      ELSE 0
      END
    ) AS FLOAT
  )/COUNT(*) AS metric_data
FROM public.account_subscription AS sub
LEFT JOIN public.account_audit AS aa
ON sub.id = aa.account_subscription_id
WHERE sub.active
AND age(NOW(), aa.date_started) < INTERVAL '7 days';