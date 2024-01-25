create table "public"."Conversation_Queue" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "conversation_id" uuid not null default gen_random_uuid()
);


CREATE UNIQUE INDEX "Message_Queue_pkey" ON public."Conversation_Queue" USING btree (id);

alter table "public"."Conversation_Queue" add constraint "Message_Queue_pkey" PRIMARY KEY using index "Message_Queue_pkey";

grant delete on table "public"."Conversation_Queue" to "anon";

grant insert on table "public"."Conversation_Queue" to "anon";

grant references on table "public"."Conversation_Queue" to "anon";

grant select on table "public"."Conversation_Queue" to "anon";

grant trigger on table "public"."Conversation_Queue" to "anon";

grant truncate on table "public"."Conversation_Queue" to "anon";

grant update on table "public"."Conversation_Queue" to "anon";

grant delete on table "public"."Conversation_Queue" to "authenticated";

grant insert on table "public"."Conversation_Queue" to "authenticated";

grant references on table "public"."Conversation_Queue" to "authenticated";

grant select on table "public"."Conversation_Queue" to "authenticated";

grant trigger on table "public"."Conversation_Queue" to "authenticated";

grant truncate on table "public"."Conversation_Queue" to "authenticated";

grant update on table "public"."Conversation_Queue" to "authenticated";

grant delete on table "public"."Conversation_Queue" to "service_role";

grant insert on table "public"."Conversation_Queue" to "service_role";

grant references on table "public"."Conversation_Queue" to "service_role";

grant select on table "public"."Conversation_Queue" to "service_role";

grant trigger on table "public"."Conversation_Queue" to "service_role";

grant truncate on table "public"."Conversation_Queue" to "service_role";

grant update on table "public"."Conversation_Queue" to "service_role";


