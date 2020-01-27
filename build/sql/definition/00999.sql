-- Add a boolean to the account_subscriptions table to indicate those accounts
-- which belong to our organisation and use in coverage reporting.
-- From: https://trello.com/c/J1Y7YFhy/180-csw-add-a-boolean-to-the-accountsubscriptions-table-to-label-those-accounts-currently-members-of-the-organisation

ALTER TABLE public.account_subscription
ADD COLUMN in_organisation BOOLEAN DEFAULT FALSE;