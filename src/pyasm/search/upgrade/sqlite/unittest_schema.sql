

-- differences
-- PRIMARY KEY line
-- now() is 'now'

CREATE TABLE city (
    id integer PRIMARY KEY AUTOINCREMENT,
    code character varying(256),
    name character varying(256),
    country_code character varying(256)
);

CREATE TABLE country (
    id integer PRIMARY KEY AUTOINCREMENT,
    code character varying(256),
    name character varying(256),
    s_status character varying(32)
);

CREATE TABLE person (
    id integer PRIMARY KEY AUTOINCREMENT,
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
    timestamp timestamp DEFAULT 'now',
    birth_date timestamp,
    pipeline_code character varying(256)
);


