-- Record exceptions by persistent resource identifier
-- Exceptions must have a user, reason and expiry date
CREATE TABLE IF NOT EXISTS resource_exception(
    id SERIAL PRIMARY KEY,
    resource_persistent_id VARCHAR(200) NOT NULL,
    criterion_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    account_subscription_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_created TIMESTAMP NOT NULL,
    date_expires TIMESTAMP NOT NULL,
    CONSTRAINT "resource_exception_criterion_id_fkey" FOREIGN KEY (criterion_id)
      REFERENCES "criterion" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "resource_exception_account_subscription_id_fkey" FOREIGN KEY (account_subscription_id)
      REFERENCES "account_subscription" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "resource_exception_user_id_fkey" FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Record whitelisted IP ranges
-- Should probably enforce a minimum bit match so you can't open to everywhere.
CREATE TABLE IF NOT EXISTS account_ssh_cidr_allowlist(
    id SERIAL PRIMARY KEY,
    cidr VARCHAR(20) NOT NULL,
    reason TEXT NOT NULL,
    account_subscription_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_created TIMESTAMP NOT NULL,
    date_expires TIMESTAMP NOT NULL,
    CONSTRAINT "account_ssh_cidr_allowlist_criterion_id_fkey" FOREIGN KEY (criterion_id)
      REFERENCES "criterion" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "account_ssh_cidr_allowlist_account_subscription_id_fkey" FOREIGN KEY (account_subscription_id)
      REFERENCES "account_subscription" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "account_ssh_cidr_allowlist_user_id_fkey" FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);