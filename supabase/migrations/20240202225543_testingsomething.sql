revoke delete on table "public"."Missed_Calls" from "anon";

revoke insert on table "public"."Missed_Calls" from "anon";

revoke references on table "public"."Missed_Calls" from "anon";

revoke select on table "public"."Missed_Calls" from "anon";

revoke trigger on table "public"."Missed_Calls" from "anon";

revoke truncate on table "public"."Missed_Calls" from "anon";

revoke update on table "public"."Missed_Calls" from "anon";

revoke delete on table "public"."Missed_Calls" from "authenticated";

revoke insert on table "public"."Missed_Calls" from "authenticated";

revoke references on table "public"."Missed_Calls" from "authenticated";

revoke select on table "public"."Missed_Calls" from "authenticated";

revoke trigger on table "public"."Missed_Calls" from "authenticated";

revoke truncate on table "public"."Missed_Calls" from "authenticated";

revoke update on table "public"."Missed_Calls" from "authenticated";

revoke delete on table "public"."Missed_Calls" from "service_role";

revoke insert on table "public"."Missed_Calls" from "service_role";

revoke references on table "public"."Missed_Calls" from "service_role";

revoke select on table "public"."Missed_Calls" from "service_role";

revoke trigger on table "public"."Missed_Calls" from "service_role";

revoke truncate on table "public"."Missed_Calls" from "service_role";

revoke update on table "public"."Missed_Calls" from "service_role";

alter table "public"."Missed_Calls" drop constraint "Missed_Calls_user_id_fkey";

alter table "public"."Missed_Calls" drop constraint "Missed Calls_pkey";

drop index if exists "public"."Missed Calls_pkey";

drop table "public"."Missed_Calls";


