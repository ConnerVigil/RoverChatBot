alter table "public"."Companies" add column "email_addresses_existing" jsonb[] default ARRAY[]::jsonb[];

alter table "public"."Companies" add column "email_addresses_new" jsonb[] default ARRAY[]::jsonb[];


