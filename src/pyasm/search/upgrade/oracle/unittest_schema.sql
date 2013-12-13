--
--


CREATE TABLE city (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    name character varying(256),
    country_code character varying(256),
    CONSTRAINT "city_code_idx" UNIQUE (code)
);



CREATE TABLE country (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    name character varying(256),
    s_status character varying(32),
    CONSTRAINT "country_code_idx" UNIQUE (code)
);





CREATE TABLE person (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    name_first character varying(100),
    name_last character varying(100),
    nationality character varying(100),
    description VARCHAR(MAX),
    picture VARCHAR(MAX),
    discussion VARCHAR(MAX),
    approval VARCHAR(MAX),
    city_code character varying(256),
    metadata VARCHAR(MAX),
    age integer,
    "timestamp" timestamp DEFAULT now(),
    birth_date timestamp,
    pipeline_code character varying(256),
    CONSTRAINT "person_code_idx" UNIQUE (code)
);


