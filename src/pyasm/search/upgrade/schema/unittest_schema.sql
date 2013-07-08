--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: postgres
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: city; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE city (
    id integer NOT NULL,
    code character varying(256),
    name character varying(256),
    country_code character varying(256)
);


ALTER TABLE public.city OWNER TO postgres;

--
-- Name: city_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE city_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.city_id_seq OWNER TO postgres;

--
-- Name: city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE city_id_seq OWNED BY city.id;


--
-- Name: country; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE country (
    id integer NOT NULL,
    code character varying(256),
    name character varying(256),
    s_status character varying(32)
);


ALTER TABLE public.country OWNER TO postgres;

--
-- Name: country_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE country_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.country_id_seq OWNER TO postgres;

--
-- Name: country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE country_id_seq OWNED BY country.id;


--
-- Name: custom_property; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE custom_property (
    id integer NOT NULL,
    search_type character varying(256),
    name character varying(256),
    description text,
    "login" character varying(256)
);


ALTER TABLE public.custom_property OWNER TO postgres;

--
-- Name: custom_property_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE custom_property_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.custom_property_id_seq OWNER TO postgres;

--
-- Name: custom_property_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE custom_property_id_seq OWNED BY custom_property.id;


--
-- Name: naming; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE naming (
    id integer NOT NULL,
    search_type character varying(100),
    dir_naming text,
    file_naming text,
    code character varying(256),
    sandbox_dir_naming text
);


ALTER TABLE public.naming OWNER TO postgres;

--
-- Name: naming_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE naming_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.naming_id_seq OWNER TO postgres;

--
-- Name: naming_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE naming_id_seq OWNED BY naming.id;


--
-- Name: person; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE person (
    id integer NOT NULL,
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
    pipeline_code character varying(256)
);


ALTER TABLE public.person OWNER TO postgres;

--
-- Name: person_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE person_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.person_id_seq OWNER TO postgres;

--
-- Name: person_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE person_id_seq OWNED BY person.id;


--
-- Name: prod_setting; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE prod_setting (
    id integer NOT NULL,
    "key" character varying(100),
    value text,
    description text,
    "type" character varying(30),
    search_type character varying(200)
);


ALTER TABLE public.prod_setting OWNER TO postgres;

--
-- Name: prod_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE prod_setting_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.prod_setting_id_seq OWNER TO postgres;

--
-- Name: prod_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE prod_setting_id_seq OWNED BY prod_setting.id;


--
-- Name: session_contents; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE session_contents (
    id integer NOT NULL,
    "login" character varying(100) NOT NULL,
    pid integer NOT NULL,
    data text,
    "session" text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.session_contents OWNER TO postgres;

--
-- Name: session_contents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE session_contents_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.session_contents_id_seq OWNER TO postgres;

--
-- Name: session_contents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE session_contents_id_seq OWNED BY session_contents.id;


--
-- Name: snapshot_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE snapshot_type (
    id integer NOT NULL,
    code character varying(256),
    pipeline_code text,
    "timestamp" timestamp without time zone DEFAULT now(),
    "login" character varying(256),
    s_status character varying(30),
    relpath text,
    project_code character varying(256),
    subcontext text,
    snapshot_flavor text
);


ALTER TABLE public.snapshot_type OWNER TO postgres;

--
-- Name: snapshot_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE snapshot_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.snapshot_type_id_seq OWNER TO postgres;

--
-- Name: snapshot_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE snapshot_type_id_seq OWNED BY snapshot_type.id;


--
-- Name: status; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE status (
    id integer NOT NULL,
    status text,
    "timestamp" timestamp without time zone DEFAULT now(),
    name character varying(128)
);


ALTER TABLE public.status OWNER TO postgres;

--
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.status_id_seq OWNER TO postgres;

--
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE status_id_seq OWNED BY status.id;


--
-- Name: widget_config; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE widget_config (
    id integer NOT NULL,
    code character varying(256),
    "view" character varying(256),
    category character varying(256),
    search_type character varying(256),
    "login" character varying(256),
    config text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32)
);


ALTER TABLE public.widget_config OWNER TO postgres;

--
-- Name: widget_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE widget_config_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.widget_config_id_seq OWNER TO postgres;

--
-- Name: widget_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE widget_config_id_seq OWNED BY widget_config.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE city ALTER COLUMN id SET DEFAULT nextval('city_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE country ALTER COLUMN id SET DEFAULT nextval('country_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE custom_property ALTER COLUMN id SET DEFAULT nextval('custom_property_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE naming ALTER COLUMN id SET DEFAULT nextval('naming_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE person ALTER COLUMN id SET DEFAULT nextval('person_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE prod_setting ALTER COLUMN id SET DEFAULT nextval('prod_setting_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE session_contents ALTER COLUMN id SET DEFAULT nextval('session_contents_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE snapshot_type ALTER COLUMN id SET DEFAULT nextval('snapshot_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE status ALTER COLUMN id SET DEFAULT nextval('status_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE widget_config ALTER COLUMN id SET DEFAULT nextval('widget_config_id_seq'::regclass);


--
-- Name: city_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY city
    ADD CONSTRAINT city_pkey PRIMARY KEY (id);


--
-- Name: code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY person
    ADD CONSTRAINT code_unique UNIQUE (code);


--
-- Name: country_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY country
    ADD CONSTRAINT country_pkey PRIMARY KEY (id);


--
-- Name: custom_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY custom_property
    ADD CONSTRAINT custom_property_pkey PRIMARY KEY (id);


--
-- Name: naming_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY naming
    ADD CONSTRAINT naming_pkey PRIMARY KEY (id);


--
-- Name: person_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);


--
-- Name: prod_setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY prod_setting
    ADD CONSTRAINT prod_setting_pkey PRIMARY KEY (id);


--
-- Name: snapshot_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY snapshot_type
    ADD CONSTRAINT snapshot_type_pkey PRIMARY KEY (id);


--
-- Name: status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- Name: widget_config_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY widget_config
    ADD CONSTRAINT widget_config_code_key UNIQUE (code);


--
-- Name: widget_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY widget_config
    ADD CONSTRAINT widget_config_pkey PRIMARY KEY (id);


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

