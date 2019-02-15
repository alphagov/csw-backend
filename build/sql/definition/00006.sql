-- Add an identifier attribute to store
ALTER TABLE public.audit_resource
ADD COLUMN resource_persistent_id VARCHAR(200);

-- Add a non-unique index to the identifier attribute
-- The LOWER function should not be necessary since the ids are created programmatically
-- it should protect against us correcting case changes like Cloudtrail to CloudTrail.
CREATE INDEX IF NOT EXISTS audit_resource_resource_persisitent_id ON public.audit_resource ((LOWER(resource_persistent_id)));
