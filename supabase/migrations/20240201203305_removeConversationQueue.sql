revoke delete on table "public"."Conversation_Queue" from "anon";

revoke insert on table "public"."Conversation_Queue" from "anon";

revoke references on table "public"."Conversation_Queue" from "anon";

revoke select on table "public"."Conversation_Queue" from "anon";

revoke trigger on table "public"."Conversation_Queue" from "anon";

revoke truncate on table "public"."Conversation_Queue" from "anon";

revoke update on table "public"."Conversation_Queue" from "anon";

revoke delete on table "public"."Conversation_Queue" from "authenticated";

revoke insert on table "public"."Conversation_Queue" from "authenticated";

revoke references on table "public"."Conversation_Queue" from "authenticated";

revoke select on table "public"."Conversation_Queue" from "authenticated";

revoke trigger on table "public"."Conversation_Queue" from "authenticated";

revoke truncate on table "public"."Conversation_Queue" from "authenticated";

revoke update on table "public"."Conversation_Queue" from "authenticated";

revoke delete on table "public"."Conversation_Queue" from "service_role";

revoke insert on table "public"."Conversation_Queue" from "service_role";

revoke references on table "public"."Conversation_Queue" from "service_role";

revoke select on table "public"."Conversation_Queue" from "service_role";

revoke trigger on table "public"."Conversation_Queue" from "service_role";

revoke truncate on table "public"."Conversation_Queue" from "service_role";

revoke update on table "public"."Conversation_Queue" from "service_role";

alter table "public"."Conversation_Queue" drop constraint "Conversation_Queue_conversation_id_fkey";

alter table "public"."Conversation_Queue" drop constraint "Message_Queue_pkey";

drop index if exists "public"."Message_Queue_pkey";

drop table "public"."Conversation_Queue";

alter table "public"."Companies" add column "JWT" text;

CREATE UNIQUE INDEX "Companies_JWT_key" ON public."Companies" USING btree ("JWT");

alter table "public"."Companies" add constraint "Companies_JWT_key" UNIQUE using index "Companies_JWT_key";


