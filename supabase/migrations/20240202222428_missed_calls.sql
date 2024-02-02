create table "public"."Missed_Calls" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "conversation_id" uuid,
    "to_phone_number" text,
    "from_phone_number" text
);


CREATE UNIQUE INDEX "Missed_Calls_pkey" ON public."Missed_Calls" USING btree (id);

alter table "public"."Missed_Calls" add constraint "Missed_Calls_pkey" PRIMARY KEY using index "Missed_Calls_pkey";

alter table "public"."Missed_Calls" add constraint "Missed_Calls_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES "Conversations"(id) not valid;

alter table "public"."Missed_Calls" validate constraint "Missed_Calls_conversation_id_fkey";

grant delete on table "public"."Missed_Calls" to "anon";

grant insert on table "public"."Missed_Calls" to "anon";

grant references on table "public"."Missed_Calls" to "anon";

grant select on table "public"."Missed_Calls" to "anon";

grant trigger on table "public"."Missed_Calls" to "anon";

grant truncate on table "public"."Missed_Calls" to "anon";

grant update on table "public"."Missed_Calls" to "anon";

grant delete on table "public"."Missed_Calls" to "authenticated";

grant insert on table "public"."Missed_Calls" to "authenticated";

grant references on table "public"."Missed_Calls" to "authenticated";

grant select on table "public"."Missed_Calls" to "authenticated";

grant trigger on table "public"."Missed_Calls" to "authenticated";

grant truncate on table "public"."Missed_Calls" to "authenticated";

grant update on table "public"."Missed_Calls" to "authenticated";

grant delete on table "public"."Missed_Calls" to "service_role";

grant insert on table "public"."Missed_Calls" to "service_role";

grant references on table "public"."Missed_Calls" to "service_role";

grant select on table "public"."Missed_Calls" to "service_role";

grant trigger on table "public"."Missed_Calls" to "service_role";

grant truncate on table "public"."Missed_Calls" to "service_role";

grant update on table "public"."Missed_Calls" to "service_role";


