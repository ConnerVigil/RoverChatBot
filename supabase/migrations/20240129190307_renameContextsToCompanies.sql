revoke delete on table "public"."Contexts" from "anon";

revoke insert on table "public"."Contexts" from "anon";

revoke references on table "public"."Contexts" from "anon";

revoke select on table "public"."Contexts" from "anon";

revoke trigger on table "public"."Contexts" from "anon";

revoke truncate on table "public"."Contexts" from "anon";

revoke update on table "public"."Contexts" from "anon";

revoke delete on table "public"."Contexts" from "authenticated";

revoke insert on table "public"."Contexts" from "authenticated";

revoke references on table "public"."Contexts" from "authenticated";

revoke select on table "public"."Contexts" from "authenticated";

revoke trigger on table "public"."Contexts" from "authenticated";

revoke truncate on table "public"."Contexts" from "authenticated";

revoke update on table "public"."Contexts" from "authenticated";

revoke delete on table "public"."Contexts" from "service_role";

revoke insert on table "public"."Contexts" from "service_role";

revoke references on table "public"."Contexts" from "service_role";

revoke select on table "public"."Contexts" from "service_role";

revoke trigger on table "public"."Contexts" from "service_role";

revoke truncate on table "public"."Contexts" from "service_role";

revoke update on table "public"."Contexts" from "service_role";

alter table "public"."Contexts" drop constraint "Contexts_pkey";

drop index if exists "public"."Contexts_pkey";

drop table "public"."Contexts";

create table "public"."Companies" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "name" text not null,
    "phone_number" text not null,
    "context" text not null
);


alter table "public"."Conversation_Queue" alter column "conversation_id" drop default;

alter table "public"."Users" add column "company_id" uuid not null;

CREATE UNIQUE INDEX "Contexts_pkey" ON public."Companies" USING btree (id);

alter table "public"."Companies" add constraint "Contexts_pkey" PRIMARY KEY using index "Contexts_pkey";

alter table "public"."Conversation_Queue" add constraint "Conversation_Queue_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES "Conversations"(id) not valid;

alter table "public"."Conversation_Queue" validate constraint "Conversation_Queue_conversation_id_fkey";

alter table "public"."Users" add constraint "Users_company_id_fkey" FOREIGN KEY (company_id) REFERENCES "Companies"(id) not valid;

alter table "public"."Users" validate constraint "Users_company_id_fkey";

grant delete on table "public"."Companies" to "anon";

grant insert on table "public"."Companies" to "anon";

grant references on table "public"."Companies" to "anon";

grant select on table "public"."Companies" to "anon";

grant trigger on table "public"."Companies" to "anon";

grant truncate on table "public"."Companies" to "anon";

grant update on table "public"."Companies" to "anon";

grant delete on table "public"."Companies" to "authenticated";

grant insert on table "public"."Companies" to "authenticated";

grant references on table "public"."Companies" to "authenticated";

grant select on table "public"."Companies" to "authenticated";

grant trigger on table "public"."Companies" to "authenticated";

grant truncate on table "public"."Companies" to "authenticated";

grant update on table "public"."Companies" to "authenticated";

grant delete on table "public"."Companies" to "service_role";

grant insert on table "public"."Companies" to "service_role";

grant references on table "public"."Companies" to "service_role";

grant select on table "public"."Companies" to "service_role";

grant trigger on table "public"."Companies" to "service_role";

grant truncate on table "public"."Companies" to "service_role";

grant update on table "public"."Companies" to "service_role";

CREATE TRIGGER testwebhook AFTER INSERT ON public."Conversation_Queue" FOR EACH ROW EXECUTE FUNCTION supabase_functions.http_request('https://doe-up-muskox.ngrok-free.app/testwebhook', 'POST', '{"Content-type":"application/json"}', '{}', '1000');


