
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '"public", "extensions"', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "public"."Conversations" (
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "user_id" uuid NOT NULL,
    "start_time" timestamp with time zone,
    "end_time" timestamp with time zone,
    "status" boolean,
    "id" uuid DEFAULT gen_random_uuid() NOT NULL
);

ALTER TABLE "public"."Conversations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Messages" (
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "content" character varying,
    "user_id" uuid NOT NULL,
    "conversation_id" uuid NOT NULL,
    "id" uuid DEFAULT gen_random_uuid() NOT NULL
);

ALTER TABLE "public"."Messages" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."Users" (
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    "phone_number" character varying,
    "first_name" character varying,
    "last_name" character varying,
    "email" character varying,
    "id" uuid DEFAULT gen_random_uuid() NOT NULL
);

ALTER TABLE "public"."Users" OWNER TO "postgres";

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Users"
    ADD CONSTRAINT "Users_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."Conversations"
    ADD CONSTRAINT "Conversations_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "Users"(id);

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES "Conversations"(id);

ALTER TABLE ONLY "public"."Messages"
    ADD CONSTRAINT "Messages_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "Users"(id);

ALTER TABLE "public"."Conversations" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable insert for users based on user_id" ON "public"."Users" FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON "public"."Users" FOR SELECT USING (true);

ALTER TABLE "public"."Messages" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."Users" ENABLE ROW LEVEL SECURITY;

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON TABLE "public"."Conversations" TO "anon";
GRANT ALL ON TABLE "public"."Conversations" TO "authenticated";
GRANT ALL ON TABLE "public"."Conversations" TO "service_role";

GRANT ALL ON TABLE "public"."Messages" TO "anon";
GRANT ALL ON TABLE "public"."Messages" TO "authenticated";
GRANT ALL ON TABLE "public"."Messages" TO "service_role";

GRANT ALL ON TABLE "public"."Users" TO "anon";
GRANT ALL ON TABLE "public"."Users" TO "authenticated";
GRANT ALL ON TABLE "public"."Users" TO "service_role";

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
