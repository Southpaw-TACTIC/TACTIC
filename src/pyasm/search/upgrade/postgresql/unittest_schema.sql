--
--


CREATE TABLE city (
    id serial PRIMARY KEY,
    code character varying(256),
    name character varying(256),
    country_code character varying(256),
    CONSTRAINT "city_code_idx" UNIQUE (code)
);



CREATE TABLE country (
    id serial PRIMARY KEY,
    code character varying(256),
    name character varying(256),
    s_status character varying(32),
    CONSTRAINT "country_code_idx" UNIQUE (code)
);





CREATE TABLE person (
    id serial PRIMARY KEY,
    code character varying(256),
    name_first character varying(100),
    name_last character varying(100),
    nationality character varying(100),
    description text,
    picture text,
    discussion text,
    approval text,
    city_code character varying(256),
    metadata text,
    age integer,
    timestamp timestamp DEFAULT now(),
    birth_date timestamp,
    pipeline_code character varying(256),
    CONSTRAINT "person_code_idx" UNIQUE (code)
);


