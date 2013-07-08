-- pg_dump -U postgres --schema-only -t naming -t custom_config -t custom_script -t custom_property  -t pref_setting -t widget_config -t prod_setting sample3d > config_schema.sql


--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

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
-- Name: custom_script; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE custom_script (
    id integer NOT NULL,
    code character varying(256),
    title character varying(256),
    description text,
    folder character varying(1024),
    script text,
    "login" character varying(256),
    "timestamp" timestamp without time zone,
    s_status character varying(256)
);


ALTER TABLE public.custom_script OWNER TO postgres;

--
-- Name: custom_script_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE custom_script_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.custom_script_id_seq OWNER TO postgres;

--
-- Name: custom_script_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE custom_script_id_seq OWNED BY custom_script.id;


--
-- Name: naming; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE naming (
    id integer NOT NULL,
    search_type character varying(100),
    dir_naming text,
    file_naming text,
    sandbox_dir_naming text,
    snapshot_type character varying(256),
    context character varying(256),
    code character varying(256),
    latest_versionless boolean,
    current_versionless boolean,
    manual_version boolean,
    ingest_rule_code character varying(256),
    condition text
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
-- Name: prod_setting; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE prod_setting (
    id integer NOT NULL,
    "key" character varying(100),
    value text,
    description text,
    "type" character varying(30),
    search_type character varying(200),
    category character varying(256)
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

ALTER TABLE custom_property ALTER COLUMN id SET DEFAULT nextval('custom_property_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE custom_script ALTER COLUMN id SET DEFAULT nextval('custom_script_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE naming ALTER COLUMN id SET DEFAULT nextval('naming_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE prod_setting ALTER COLUMN id SET DEFAULT nextval('prod_setting_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE widget_config ALTER COLUMN id SET DEFAULT nextval('widget_config_id_seq'::regclass);


--
-- Name: custom_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY custom_property
    ADD CONSTRAINT custom_property_pkey PRIMARY KEY (id);


--
-- Name: custom_script_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY custom_script
    ADD CONSTRAINT custom_script_pkey PRIMARY KEY (id);


--
-- Name: key_search_type_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY prod_setting
    ADD CONSTRAINT key_search_type_unique UNIQUE ("key", search_type);


--
-- Name: naming_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY naming
    ADD CONSTRAINT naming_pkey PRIMARY KEY (id);


--
-- Name: prod_setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY prod_setting
    ADD CONSTRAINT prod_setting_pkey PRIMARY KEY (id);


--
-- Name: widget_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY widget_config
    ADD CONSTRAINT widget_config_pkey PRIMARY KEY (id);


--
-- Name: prod_setting_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX prod_setting_name_idx ON prod_setting USING btree ("key");


--
-- Name: widget_config_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX widget_config_code_idx ON widget_config USING btree (code);


--
-- Name: spt_url; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE spt_url (
    id integer NOT NULL,
    code character varying(256),
    url character varying(256),
    widget text,
    description text,
    "timestamp" timestamp without time zone,
    s_status character varying(256)
);


ALTER TABLE public.spt_url OWNER TO postgres;

--
-- Name: spt_url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spt_url_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spt_url_id_seq OWNER TO postgres;

--
-- Name: spt_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spt_url_id_seq OWNED BY spt_url.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE spt_url ALTER COLUMN id SET DEFAULT nextval('spt_url_id_seq'::regclass);


--
-- Name: spt_url_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY spt_url
    ADD CONSTRAINT spt_url_pkey PRIMARY KEY (id);


--
-- Name: spt_client_trigger; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE spt_client_trigger (
    id integer NOT NULL,
    code character varying(256),
    event character varying(256),
    callback character varying(256),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32)
);


ALTER TABLE public.spt_client_trigger OWNER TO postgres;

--
-- Name: spt_client_trigger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spt_client_trigger_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spt_client_trigger_id_seq OWNER TO postgres;

--
-- Name: spt_client_trigger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spt_client_trigger_id_seq OWNED BY spt_client_trigger.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE spt_client_trigger ALTER COLUMN id SET DEFAULT nextval('spt_client_trigger_id_seq'::regclass);


--
-- Name: spt_client_trigger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY spt_client_trigger
    ADD CONSTRAINT spt_client_trigger_pkey PRIMARY KEY (id);



--
-- Name: spt_plugin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--
CREATE TABLE spt_plugin (
    id integer NOT NULL,
    code varchar(256),
    version varchar(256),
    description text,
    manifest text,
    timestamp timestamp,
    s_status varchar(256)
);




ALTER TABLE public.spt_plugin OWNER TO postgres;

--
-- Name: spt_plugin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spt_plugin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spt_plugin_id_seq OWNER TO postgres;

--
-- Name: spt_plugin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spt_plugin_id_seq OWNED BY spt_plugin.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE spt_plugin ALTER COLUMN id SET DEFAULT nextval('spt_plugin_id_seq'::regclass);


--
-- Name: spt_plugin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY spt_plugin
    ADD CONSTRAINT spt_plugin_pkey PRIMARY KEY (id);




--
-- Name: spt_trigger; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE spt_trigger (
    id integer NOT NULL,
    code varchar(256),
    class_name varchar(256),
    script_path varchar(256),
    title varchar(256),
    description text,
    event varchar(256),
    mode varchar(256),
    process varchar(256),
    listen_process varchar(256),
    trigger_type varchar(256),
    data text,
    timestamp timestamp,
    s_status varchar(256)
);



ALTER TABLE public.spt_trigger OWNER TO postgres;



--
-- Name: spt_trigger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spt_trigger_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spt_trigger_id_seq OWNER TO postgres;

--
-- Name: spt_trigger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spt_trigger_id_seq OWNED BY spt_trigger.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE spt_trigger ALTER COLUMN id SET DEFAULT nextval('spt_trigger_id_seq'::regclass);


--
-- Name: spt_trigger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY spt_trigger
    ADD CONSTRAINT spt_trigger_pkey PRIMARY KEY (id);






--
-- Name: spt_process; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE spt_process (
    id integer NOT NULL,
    code varchar(256),
    pipeline_code varchar(256),
    process varchar(256),
    color varchar(256),
    sort_order integer,
    timestamp timestamp,
    context_options text,
    subcontext_options text,
    checkin_mode text,
    checkin_validate_script_path text,
    sandbox_create_script_path text,
    s_status varchar(256)
);



ALTER TABLE public.spt_process OWNER TO postgres;



--
-- Name: spt_process_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE spt_process_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.spt_process_id_seq OWNER TO postgres;

--
-- Name: spt_process_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE spt_process_id_seq OWNED BY spt_process.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE spt_process ALTER COLUMN id SET DEFAULT nextval('spt_process_id_seq'::regclass);


--
-- Name: spt_process_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY spt_process
    ADD CONSTRAINT spt_process_pkey PRIMARY KEY (id);



--
-- PostgreSQL database dump complete
--

