create type "public"."role" as enum ('user', 'assistant');

alter table "public"."Messages" add column "role" role not null;


