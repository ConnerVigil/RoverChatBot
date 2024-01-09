create table "public"."Contexts" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "company_name" text not null,
    "company_phone_number" text not null,
    "content" text not null
);


alter table "public"."Contexts" enable row level security;

alter table "public"."Conversations" drop column "end_time";

alter table "public"."Conversations" drop column "start_time";

alter table "public"."Conversations" drop column "status";

alter table "public"."Users" alter column "email" set data type text using "email"::text;

alter table "public"."Users" alter column "first_name" set data type text using "first_name"::text;

alter table "public"."Users" alter column "last_name" set data type text using "last_name"::text;

alter table "public"."Users" alter column "phone_number" set data type text using "phone_number"::text;

CREATE UNIQUE INDEX "Contexts_pkey" ON public."Contexts" USING btree (id);

alter table "public"."Contexts" add constraint "Contexts_pkey" PRIMARY KEY using index "Contexts_pkey";

grant delete on table "public"."Contexts" to "anon";

grant insert on table "public"."Contexts" to "anon";

grant references on table "public"."Contexts" to "anon";

grant select on table "public"."Contexts" to "anon";

grant trigger on table "public"."Contexts" to "anon";

grant truncate on table "public"."Contexts" to "anon";

grant update on table "public"."Contexts" to "anon";

grant delete on table "public"."Contexts" to "authenticated";

grant insert on table "public"."Contexts" to "authenticated";

grant references on table "public"."Contexts" to "authenticated";

grant select on table "public"."Contexts" to "authenticated";

grant trigger on table "public"."Contexts" to "authenticated";

grant truncate on table "public"."Contexts" to "authenticated";

grant update on table "public"."Contexts" to "authenticated";

grant delete on table "public"."Contexts" to "service_role";

grant insert on table "public"."Contexts" to "service_role";

grant references on table "public"."Contexts" to "service_role";

grant select on table "public"."Contexts" to "service_role";

grant trigger on table "public"."Contexts" to "service_role";

grant truncate on table "public"."Contexts" to "service_role";

grant update on table "public"."Contexts" to "service_role";


