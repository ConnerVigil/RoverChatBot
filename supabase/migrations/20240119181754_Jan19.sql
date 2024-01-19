alter type "public"."role" rename to "role__old_version_to_be_dropped";

create type "public"."role" as enum ('user', 'assistant', 'tool');

alter table "public"."Messages" alter column role type "public"."role" using role::text::"public"."role";

drop type "public"."role__old_version_to_be_dropped";

alter table "public"."Messages" add column "function_name" text;

alter table "public"."Messages" add column "tool_call_id" text;

alter table "public"."Messages" add column "tool_calls" jsonb[] not null default ARRAY[]::jsonb[];


