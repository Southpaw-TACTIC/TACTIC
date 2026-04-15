--
--


CREATE TABLE "city" (
    "id" integer PRIMARY KEY AUTOINCREMENT,
    "code" character varying(256),
    "name" character varying(256),
    "country_code" character varying(256),
    CONSTRAINT "city_code_idx" UNIQUE ("code")
);



CREATE TABLE "country" (
    "id" integer PRIMARY KEY AUTOINCREMENT,
    "code" character varying(256),
    "name" character varying(256),
    "s_status" character varying(32),
    CONSTRAINT "country_code_idx" UNIQUE ("code")
);





CREATE TABLE "person" (
    "id" integer PRIMARY KEY AUTOINCREMENT,
    "code" character varying(256),
    "name_first" character varying(100),
    "name_last" character varying(100),
    "nationality" character varying(100),
    "description" text,
    "picture" text,
    "discussion" text,
    "approval" text,
    "city_code" character varying(256),
    "metadata" text,
    "age" integer,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP,
    "birth_date" timestamp,
    "pipeline_code" character varying(256),
    CONSTRAINT "person_code_idx" UNIQUE ("code")
);


CREATE TABLE "person_in_car" (
    "id" integer PRIMARY KEY AUTOINCREMENT,
    "code" character varying(256),
    "person_code" character varying(256),
    "car_code" character varying(256),
    CONSTRAINT "person_in_car_code_idx" UNIQUE ("code")
);


CREATE TABLE "car" (
    "id" integer PRIMARY KEY AUTOINCREMENT,
    "code" character varying(256),
    "model" character varying(256),
    CONSTRAINT "person_code_idx" UNIQUE ("code")
);




