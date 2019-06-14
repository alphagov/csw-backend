-- Create a default team to assign new account subscriptions to
-- These should be monitored and added to a real team.
INSERT INTO public.product_team (team_name, active)
VALUES ('TBC', true);

-- Add properties to account subscription table to record
-- reason for inactive accounts
ALTER TABLE public.account_subscription
ADD COLUMN suspended BOOLEAN DEFAULT FALSE;

ALTER TABLE public.account_subscription
ADD COLUMN auditable BOOLEAN DEFAULT FALSE;

ALTER TABLE public.account_subscription
ADD CONSTRAINT account_subscription_account_id UNIQUE (account_id);