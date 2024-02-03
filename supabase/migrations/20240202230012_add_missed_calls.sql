
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pg_net" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

CREATE TYPE "public"."role" AS ENUM (
    'user',
    'assistant',
    'tool'
);

ALTER TYPE "public"."role" OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "public"."Companies" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text" NOT NULL,
    "phone_number" "text" NOT NULL,
    "context" "text" NOT NULL,
    "JWT" "text"
);

ALTER TABLE "public"."Companies" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Conversations" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);

ALTER TABLE "public"."Conversations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Messages" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "content" "text",
    "user_id" "uuid" NOT NULL,
    "conversation_id" "uuid" NOT NULL,
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "role" "public"."role" NOT NULL,
    "function_name" "text",
    "tool_call_id" "text",
    "tool_calls" "jsonb"[] DEFAULT ARRAY[]::"jsonb"[] NOT NULL
);

ALTER TABLE "public"."Messages" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Missed_Calls" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "conversation_id" "uuid" NOT NULL,
    "to_phone_number" "text" NOT NULL,
    "from_phone_number" "text" NOT NULL
);

ALTER TABLE "public"."Missed_Calls" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Users" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "phone_number" "text",
    "first_name" "text",
    "last_name" "text",
    "email" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "company_id" "uuid"
);

ALTER TABLE "public"."Users" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Waitlist" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "first_name" "text",
    "last_name" "text",
    "email" "text"
);

ALTER TABLE "public"."Waitlist" OWNER TO "postgres";

ALTER TABLE "public"."Waitlist" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."Waitlist_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY "public"."Companies"
    ADD CONSTRAINT "Companies_JWT_key" UNIQUE ("JWT");

ALTER TABLE ONLY "public"."Companies"
    ADD CONSTRAINT "Contexts_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Missed_Calls"
    ADD CONSTRAINT "Missed_Calls_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Users"
    ADD CONSTRAINT "Users_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Waitlist"
    ADD CONSTRAINT "Waitlist_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."Users"("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "public"."Conversations"("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."Users"("id");

ALTER TABLE ONLY "public"."Missed_Calls"
    ADD CONSTRAINT "Missed_Calls_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "public"."Conversations"("id");

ALTER TABLE ONLY "public"."Users"
    ADD CONSTRAINT "Users_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."Companies"("id");

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON TABLE "public"."Companies" TO "anon";
GRANT ALL ON TABLE "public"."Companies" TO "authenticated";
GRANT ALL ON TABLE "public"."Companies" TO "service_role";

GRANT ALL ON TABLE "public"."Conversations" TO "anon";
GRANT ALL ON TABLE "public"."Conversations" TO "authenticated";
GRANT ALL ON TABLE "public"."Conversations" TO "service_role";

GRANT ALL ON TABLE "public"."Messages" TO "anon";
GRANT ALL ON TABLE "public"."Messages" TO "authenticated";
GRANT ALL ON TABLE "public"."Messages" TO "service_role";

GRANT ALL ON TABLE "public"."Missed_Calls" TO "anon";
GRANT ALL ON TABLE "public"."Missed_Calls" TO "authenticated";
GRANT ALL ON TABLE "public"."Missed_Calls" TO "service_role";

GRANT ALL ON TABLE "public"."Users" TO "anon";
GRANT ALL ON TABLE "public"."Users" TO "authenticated";
GRANT ALL ON TABLE "public"."Users" TO "service_role";

GRANT ALL ON TABLE "public"."Waitlist" TO "anon";
GRANT ALL ON TABLE "public"."Waitlist" TO "authenticated";
GRANT ALL ON TABLE "public"."Waitlist" TO "service_role";

GRANT ALL ON SEQUENCE "public"."Waitlist_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."Waitlist_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."Waitlist_id_seq" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
