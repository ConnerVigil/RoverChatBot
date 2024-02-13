alter table "public"."Companies" drop constraint "Companies_JWT_key";

drop index if exists "public"."Companies_JWT_key";

alter table "public"."Companies" drop column "JWT";

alter table "public"."Companies" add column "close_time_utc" time without time zone;

alter table "public"."Companies" add column "open_time_utc" time without time zone;


