--
-- PostgreSQL database dump
--

SET client_encoding = 'SQL_ASCII';
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: custom_property; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE custom_property (
    id serial NOT NULL,
    search_type character varying(256),
    name character varying(256),
    description text,
    "login" character varying(256)
);


ALTER TABLE public.custom_property OWNER TO postgres;

--
-- Name: naming; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE naming (
    id serial NOT NULL,
    search_type character varying(100),
    dir_naming text,
    file_naming text
);


ALTER TABLE public.naming OWNER TO postgres;

--
-- Name: person; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE person (
    id serial NOT NULL,
    code character varying(256),
    name_first character varying(100),
    name_last character varying(100),
    nationality character varying(100),
    description text,
    picture text,
    discussion text,
    approval text,
    city_code character varying(256)
);


ALTER TABLE public.person OWNER TO postgres;


CREATE TABLE city (
    id serial NOT NULL,
    code character varying(256),
    name character varying(256),
    country_code character varying(256),
    s_status character varying(32)
);

CREATE TABLE country (
    id serial NOT NULL,
    code character varying(256),
    name character varying(256),
    s_status character varying(32)
);


--
-- Name: prod_setting; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE prod_setting (
    id serial NOT NULL,
    "code" character varying(256),
    "key" character varying(100),
    value text,
    description text,
    "type" character varying(30),
    search_type character varying(200)
);


ALTER TABLE public.prod_setting OWNER TO postgres;

--
-- Name: status; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE status (
    id serial NOT NULL,
    status text,
    "timestamp" timestamp without time zone DEFAULT now(),
    name character varying(128)
);


ALTER TABLE public.status OWNER TO postgres;

--
-- Name: custom_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY custom_property
    ADD CONSTRAINT custom_property_pkey PRIMARY KEY (id);


--
-- Name: status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

