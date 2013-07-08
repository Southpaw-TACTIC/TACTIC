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


SET search_path = public, pg_catalog;

--
-- Name: plpgsql_call_handler(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    AS '$libdir/plpgsql', 'plpgsql_call_handler'
    LANGUAGE c;


ALTER FUNCTION public.plpgsql_call_handler() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: art_reference; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE art_reference (
    id integer NOT NULL,
    name_old character varying(256),
    description text,
    snapshot text,
    category character varying(256),
    s_status character varying(30),
    keywords text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.art_reference OWNER TO postgres;

--
-- Name: art_reference_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE art_reference_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.art_reference_id_seq OWNER TO postgres;

--
-- Name: art_reference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE art_reference_id_seq OWNED BY art_reference.id;


--
-- Name: asset; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset (
    id integer NOT NULL,
    code character varying(256),
    name character varying(256),
    asset_type character varying(30),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    images text,
    status text,
    snapshot text,
    retire_status character varying(30),
    asset_library character varying(100),
    pipeline_code character varying(256),
    s_status character varying(30),
    short_code character varying(256)
);


ALTER TABLE public.asset OWNER TO postgres;

--
-- Name: asset_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE asset_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.asset_id_seq OWNER TO postgres;

--
-- Name: asset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE asset_id_seq OWNED BY asset.id;


--
-- Name: asset_library; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset_library (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    title character varying(100),
    description text,
    padding smallint,
    "type" character varying(30),
    s_status character varying(30)
);


ALTER TABLE public.asset_library OWNER TO postgres;

--
-- Name: asset_library_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE asset_library_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.asset_library_id_seq OWNER TO postgres;

--
-- Name: asset_library_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE asset_library_id_seq OWNED BY asset_library.id;


--
-- Name: asset_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset_type (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description text
);


ALTER TABLE public.asset_type OWNER TO postgres;

--
-- Name: asset_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE asset_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.asset_type_id_seq OWNER TO postgres;

--
-- Name: asset_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE asset_type_id_seq OWNED BY asset_type.id;


--
-- Name: bin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE bin (
    id integer NOT NULL,
    code character varying(256),
    description text,
    "type" character varying(100),
    s_status character varying(30),
    label character varying(100)
);


ALTER TABLE public.bin OWNER TO postgres;

--
-- Name: bin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE bin_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.bin_id_seq OWNER TO postgres;

--
-- Name: bin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE bin_id_seq OWNED BY bin.id;


--
-- Name: camera; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE camera (
    id integer NOT NULL,
    shot_code character varying(30),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30)
);


ALTER TABLE public.camera OWNER TO postgres;

--
-- Name: camera_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE camera_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.camera_id_seq OWNER TO postgres;

--
-- Name: camera_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE camera_id_seq OWNED BY camera.id;


--
-- Name: composite; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE composite (
    id integer NOT NULL,
    name character varying(100),
    description text,
    shot_code character varying(100),
    snapshot text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.composite OWNER TO postgres;

--
-- Name: composite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE composite_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.composite_id_seq OWNER TO postgres;

--
-- Name: composite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE composite_id_seq OWNED BY composite.id;



--
-- Name: cut_sequence; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cut_sequence (
    id integer NOT NULL,
    shot_code character varying(30),
    "type" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    description text,
    sequence_code character varying(100)
);


ALTER TABLE public.cut_sequence OWNER TO postgres;

--
-- Name: cut_sequence_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE cut_sequence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.cut_sequence_id_seq OWNER TO postgres;

--
-- Name: cut_sequence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE cut_sequence_id_seq OWNED BY cut_sequence.id;


--
-- Name: episode; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE episode (
    id integer NOT NULL,
    code character varying(256) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    sort_order smallint
);


ALTER TABLE public.episode OWNER TO postgres;

--
-- Name: episode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE episode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.episode_id_seq OWNER TO postgres;

--
-- Name: episode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE episode_id_seq OWNED BY episode.id;


--
-- Name: geo_cache; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE geo_cache (
    id integer NOT NULL,
    shot_code character varying(256),
    instance character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30)
);


ALTER TABLE public.geo_cache OWNER TO postgres;

--
-- Name: geo_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE geo_cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.geo_cache_id_seq OWNER TO postgres;

--
-- Name: geo_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE geo_cache_id_seq OWNED BY geo_cache.id;


--
-- Name: instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE instance (
    id integer NOT NULL,
    code character varying(256),
    shot_code character varying(30) NOT NULL,
    asset_code character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    "type" character varying(30)
);


ALTER TABLE public.instance OWNER TO postgres;

--
-- Name: instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE instance_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.instance_id_seq OWNER TO postgres;

--
-- Name: instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE instance_id_seq OWNED BY instance.id;


--
-- Name: layer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE layer (
    id integer NOT NULL,
    name character varying(100),
    description text,
    shot_code character varying(100),
    snapshot text,
    "timestamp" timestamp without time zone DEFAULT now(),
    sort_order integer,
    s_status character varying(30)
);


ALTER TABLE public.layer OWNER TO postgres;

--
-- Name: layer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE layer_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.layer_id_seq OWNER TO postgres;

--
-- Name: layer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE layer_id_seq OWNED BY layer.id;


--
-- Name: layer_instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE layer_instance (
    id integer NOT NULL,
    asset_code character varying(100),
    "type" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    name character varying(100),
    layer_id integer
);


ALTER TABLE public.layer_instance OWNER TO postgres;

--
-- Name: layer_instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE layer_instance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.layer_instance_id_seq OWNER TO postgres;

--
-- Name: layer_instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE layer_instance_id_seq OWNED BY layer_instance.id;





--
-- Name: pga_forms; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_forms (
    formname character varying(64),
    formsource text
);


ALTER TABLE public.pga_forms OWNER TO postgres;

--
-- Name: pga_layout; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_layout (
    tablename character varying(64),
    nrcols smallint,
    colnames text,
    colwidth text
);


ALTER TABLE public.pga_layout OWNER TO postgres;

--
-- Name: pga_queries; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_queries (
    queryname character varying(64),
    querytype character(1),
    querycommand text,
    querytables text,
    querylinks text,
    queryresults text,
    querycomments text
);


ALTER TABLE public.pga_queries OWNER TO postgres;

--
-- Name: pga_reports; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_reports (
    reportname character varying(64),
    reportsource text,
    reportbody text,
    reportprocs text,
    reportoptions text
);


ALTER TABLE public.pga_reports OWNER TO postgres;

--
-- Name: pga_schema; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_schema (
    schemaname character varying(64),
    schematables text,
    schemalinks text
);


ALTER TABLE public.pga_schema OWNER TO postgres;

--
-- Name: pga_scripts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_scripts (
    scriptname character varying(64),
    scriptsource text
);


ALTER TABLE public.pga_scripts OWNER TO postgres;

--
-- Name: plate; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plate (
    id integer NOT NULL,
    shot_code character varying(30),
    "type" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    description text,
    code character varying(256),
    pipeline_code character varying(256)
);


ALTER TABLE public.plate OWNER TO postgres;

--
-- Name: plate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE plate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.plate_id_seq OWNER TO postgres;

--
-- Name: plate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE plate_id_seq OWNED BY plate.id;


--
-- Name: process; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE process (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.process OWNER TO postgres;

--
-- Name: process_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE process_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.process_id_seq OWNER TO postgres;

--
-- Name: process_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE process_id_seq OWNED BY process.id;


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
-- Name: render; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE render (
    id integer NOT NULL,
    _images text,
    _session text,
    "login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now(),
    _snapshot text,
    search_type character varying(100),
    search_id integer,
    _snapshot_code character varying(30),
    _version smallint,
    _file_range character varying(200),
    code character varying(256),
    "type" character varying(256),
    name character varying(256),
    s_status character varying(30)
);


ALTER TABLE public.render OWNER TO postgres;

--
-- Name: render_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE render_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.render_id_seq OWNER TO postgres;

--
-- Name: render_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE render_id_seq OWNED BY render.id;


--
-- Name: render_stage; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE render_stage (
    id integer NOT NULL,
    search_type character varying(100),
    search_id integer,
    context character varying(30),
    snapshot text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.render_stage OWNER TO postgres;

--
-- Name: render_stage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE render_stage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.render_stage_id_seq OWNER TO postgres;

--
-- Name: render_stage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE render_stage_id_seq OWNED BY render_stage.id;

--
-- Name: render_policy; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE render_policy (
    id integer NOT NULL,
    code character varying(30),
    description text,
    width smallint,
    height smallint,
    frame_by smallint,
    extra_settings text
);


ALTER TABLE public.render_policy OWNER TO postgres;

--
-- Name: render_policy_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE render_policy_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.render_policy_id_seq OWNER TO postgres;

--
-- Name: render_policy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE render_policy_id_seq OWNED BY render_policy.id;


--
-- Name: render_policy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('render_policy_id_seq', 1, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE render_policy ALTER COLUMN id SET DEFAULT nextval('render_policy_id_seq'::regclass);


--
-- Name: script; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE script (
    id integer NOT NULL,
    files text,
    "timestamp" timestamp without time zone DEFAULT now(),
    code character varying(30),
    description text,
    sequence_code character varying(30),
    stage character varying(256),
    title text,
    author character varying(256)
);


ALTER TABLE public.script OWNER TO postgres;

--
-- Name: script_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE script_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.script_id_seq OWNER TO postgres;

--
-- Name: script_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE script_id_seq OWNED BY script.id;


--
-- Name: sequence; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "sequence" (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    sort_order smallint,
    episode_code character varying(256)
);


ALTER TABLE public."sequence" OWNER TO postgres;

--
-- Name: sequence_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE sequence_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.sequence_id_seq OWNER TO postgres;

--
-- Name: sequence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE sequence_id_seq OWNED BY "sequence".id;


--
-- Name: sequence_instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sequence_instance (
    id integer NOT NULL,
    sequence_code character varying(30) NOT NULL,
    asset_code character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    "type" character varying(30)
);


ALTER TABLE public.sequence_instance OWNER TO postgres;

--
-- Name: sequence_instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE sequence_instance_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.sequence_instance_id_seq OWNER TO postgres;

--
-- Name: sequence_instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE sequence_instance_id_seq OWNED BY sequence_instance.id;


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
-- Name: shot; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    images text,
    tc_frame_start integer DEFAULT 1,
    tc_frame_end integer DEFAULT 1,
    pipeline_code character varying(30),
    s_status character varying(30),
    parent_code character varying(30),
    sequence_code character varying(30),
    sort_order smallint,
    complexity smallint,
    frame_in integer,
    frame_out integer,
    frame_note text,
    scan_status character varying(256),
    "type" character varying(256),
    priority character varying(30),
    short_code character varying(256)
);


ALTER TABLE public.shot OWNER TO postgres;

--
-- Name: shot_audio; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_audio (
    id integer NOT NULL,
    title character varying(30),
    shot_code character varying(100)
);


ALTER TABLE public.shot_audio OWNER TO postgres;

--
-- Name: shot_audio_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE shot_audio_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.shot_audio_id_seq OWNER TO postgres;

--
-- Name: shot_audio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE shot_audio_id_seq OWNED BY shot_audio.id;


--
-- Name: shot_definition; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_definition (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    pipeline character varying(30) NOT NULL
);


ALTER TABLE public.shot_definition OWNER TO postgres;

--
-- Name: shot_definition_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE shot_definition_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.shot_definition_id_seq OWNER TO postgres;

--
-- Name: shot_definition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE shot_definition_id_seq OWNED BY shot_definition.id;


--
-- Name: shot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE shot_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.shot_id_seq OWNER TO postgres;

--
-- Name: shot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE shot_id_seq OWNED BY shot.id;


--
-- Name: shot_texture; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_texture (
    id integer NOT NULL,
    description text,
    shot_code character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    snapshot text,
    s_status character varying(32),
    code character varying(256),
    pipeline_code character varying(256),
    asset_context character varying(256),
    search_type character varying(256),
    search_id integer
);


ALTER TABLE public.shot_texture OWNER TO postgres;

--
-- Name: shot_texture_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE shot_texture_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.shot_texture_id_seq OWNER TO postgres;

--
-- Name: shot_texture_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE shot_texture_id_seq OWNED BY shot_texture.id;


--
-- Name: storyboard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE storyboard (
    id integer NOT NULL,
    files text,
    "timestamp" timestamp without time zone DEFAULT now(),
    code character varying(30),
    shot_code character varying(30),
    description text
);


ALTER TABLE public.storyboard OWNER TO postgres;

--
-- Name: storyboard_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE storyboard_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.storyboard_id_seq OWNER TO postgres;

--
-- Name: storyboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE storyboard_id_seq OWNED BY storyboard.id;


--
-- Name: submission; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE submission (
    id integer NOT NULL,
    code character varying(256),
    search_type character varying(200),
    search_id integer,
    snapshot_code character varying(30),
    context character varying(100),
    version integer,
    description text,
    "login" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    artist character varying(256),
    status character varying(100)
);


ALTER TABLE public.submission OWNER TO postgres;

--
-- Name: submission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE submission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.submission_id_seq OWNER TO postgres;

--
-- Name: submission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE submission_id_seq OWNED BY submission.id;


--
-- Name: submission_in_bin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE submission_in_bin (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    bin_id integer NOT NULL
);


ALTER TABLE public.submission_in_bin OWNER TO postgres;

--
-- Name: submission_in_bin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE submission_in_bin_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.submission_in_bin_id_seq OWNER TO postgres;

--
-- Name: submission_in_bin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE submission_in_bin_id_seq OWNED BY submission_in_bin.id;




--
-- Name: texture; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE texture (
    id integer NOT NULL,
    description text,
    asset_code character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    snapshot text,
    s_status character varying(32),
    code character varying(256),
    pipeline_code character varying(256),
    asset_context character varying(256)
);


ALTER TABLE public.texture OWNER TO postgres;

--
-- Name: texture_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE texture_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.texture_id_seq OWNER TO postgres;

--
-- Name: texture_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE texture_id_seq OWNED BY texture.id;



--
-- Name: texture_asset_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX texture_asset_code_idx ON texture USING btree (asset_code);


--
-- Name: texture_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX texture_code_idx ON texture USING btree (code);





--
-- Name: texture_source; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE texture_source (
    id integer NOT NULL,
    description text,
    asset_code character varying(50),
    category character varying(200),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32),
    code character varying(100)
);


ALTER TABLE public.texture_source OWNER TO postgres;

--
-- Name: texture_source_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE texture_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.texture_source_id_seq OWNER TO postgres;

--
-- Name: texture_source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE texture_source_id_seq OWNED BY texture_source.id;


--
-- widget config table
--
CREATE TABLE widget_config (
    id serial,
    code character varying(256),
    "view" character varying(256),
    category character varying(256),
    search_type character varying(256),
    "login" character varying(256),
    config text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32),
    PRIMARY KEY (id)
);





--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE art_reference ALTER COLUMN id SET DEFAULT nextval('art_reference_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE asset ALTER COLUMN id SET DEFAULT nextval('asset_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE asset_library ALTER COLUMN id SET DEFAULT nextval('asset_library_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE asset_type ALTER COLUMN id SET DEFAULT nextval('asset_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE bin ALTER COLUMN id SET DEFAULT nextval('bin_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE camera ALTER COLUMN id SET DEFAULT nextval('camera_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE composite ALTER COLUMN id SET DEFAULT nextval('composite_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE custom_property ALTER COLUMN id SET DEFAULT nextval('custom_property_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE cut_sequence ALTER COLUMN id SET DEFAULT nextval('cut_sequence_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE episode ALTER COLUMN id SET DEFAULT nextval('episode_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE geo_cache ALTER COLUMN id SET DEFAULT nextval('geo_cache_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE instance ALTER COLUMN id SET DEFAULT nextval('instance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE layer ALTER COLUMN id SET DEFAULT nextval('layer_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE layer_instance ALTER COLUMN id SET DEFAULT nextval('layer_instance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE naming ALTER COLUMN id SET DEFAULT nextval('naming_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE plate ALTER COLUMN id SET DEFAULT nextval('plate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE process ALTER COLUMN id SET DEFAULT nextval('process_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE prod_setting ALTER COLUMN id SET DEFAULT nextval('prod_setting_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE render ALTER COLUMN id SET DEFAULT nextval('render_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE render_stage ALTER COLUMN id SET DEFAULT nextval('render_stage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE script ALTER COLUMN id SET DEFAULT nextval('script_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "sequence" ALTER COLUMN id SET DEFAULT nextval('sequence_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE sequence_instance ALTER COLUMN id SET DEFAULT nextval('sequence_instance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE session_contents ALTER COLUMN id SET DEFAULT nextval('session_contents_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE shot ALTER COLUMN id SET DEFAULT nextval('shot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE shot_audio ALTER COLUMN id SET DEFAULT nextval('shot_audio_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE shot_definition ALTER COLUMN id SET DEFAULT nextval('shot_definition_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE shot_texture ALTER COLUMN id SET DEFAULT nextval('shot_texture_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE storyboard ALTER COLUMN id SET DEFAULT nextval('storyboard_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE submission ALTER COLUMN id SET DEFAULT nextval('submission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE submission_in_bin ALTER COLUMN id SET DEFAULT nextval('submission_in_bin_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE texture ALTER COLUMN id SET DEFAULT nextval('texture_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE texture_source ALTER COLUMN id SET DEFAULT nextval('texture_source_id_seq'::regclass);


--
-- Name: art_reference_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY art_reference
    ADD CONSTRAINT art_reference_pkey PRIMARY KEY (id);


--
-- Name: asset_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY asset
    ADD CONSTRAINT asset_code_key UNIQUE (code);


--
-- Name: asset_library_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY asset_library
    ADD CONSTRAINT asset_library_pkey PRIMARY KEY (code);


--
-- Name: asset_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY asset
    ADD CONSTRAINT asset_name_key UNIQUE (name);


--
-- Name: asset_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY asset
    ADD CONSTRAINT asset_pkey PRIMARY KEY (code);


--
-- Name: asset_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY asset_type
    ADD CONSTRAINT asset_type_pkey PRIMARY KEY (code);


--
-- Name: bin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bin
    ADD CONSTRAINT bin_pkey PRIMARY KEY (id);


--
-- Name: camera_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY camera
    ADD CONSTRAINT camera_pkey PRIMARY KEY (id);


--
-- Name: composite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY composite
    ADD CONSTRAINT composite_pkey PRIMARY KEY (id);


--
-- Name: custom_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY custom_property
    ADD CONSTRAINT custom_property_pkey PRIMARY KEY (id);


--
-- Name: cut_sequence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY cut_sequence
    ADD CONSTRAINT cut_sequence_pkey PRIMARY KEY (id);


--
-- Name: episode_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY episode
    ADD CONSTRAINT episode_code_unique UNIQUE (code);


--
-- Name: geo_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY geo_cache
    ADD CONSTRAINT geo_cache_pkey PRIMARY KEY (id);


--
-- Name: instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT instance_pkey PRIMARY KEY (id);


--
-- Name: instance_shot_code_type_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT instance_shot_code_type_key UNIQUE (shot_code, name, "type");


--
-- Name: key_search_type_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY prod_setting
    ADD CONSTRAINT key_search_type_unique UNIQUE ("key", search_type);


--
-- Name: layer_instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY layer_instance
    ADD CONSTRAINT layer_instance_pkey PRIMARY KEY (id);


--
-- Name: layer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY layer
    ADD CONSTRAINT layer_pkey PRIMARY KEY (id);


--
-- Name: layer_shot_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY layer
    ADD CONSTRAINT layer_shot_code_key UNIQUE (shot_code, name);


--
-- Name: naming_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY naming
    ADD CONSTRAINT naming_pkey PRIMARY KEY (id);


--
-- Name: plate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY plate
    ADD CONSTRAINT plate_pkey PRIMARY KEY (id);


--
-- Name: process_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY process
    ADD CONSTRAINT process_code_key UNIQUE (code);


--
-- Name: process_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY process
    ADD CONSTRAINT process_pkey PRIMARY KEY (code);


--
-- Name: prod_setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY prod_setting
    ADD CONSTRAINT prod_setting_pkey PRIMARY KEY (id);


--
-- Name: render_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY render
    ADD CONSTRAINT render_pkey PRIMARY KEY (id);


--
-- Name: render_stage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY render_stage
    ADD CONSTRAINT render_stage_pkey PRIMARY KEY (id);


--
-- Name: script_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY script
    ADD CONSTRAINT script_pkey PRIMARY KEY (id);


--
-- Name: sequence_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "sequence"
    ADD CONSTRAINT sequence_code_key UNIQUE (code);


--
-- Name: sequence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "sequence"
    ADD CONSTRAINT sequence_pkey PRIMARY KEY (code);


--
-- Name: session_contents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY session_contents
    ADD CONSTRAINT session_contents_pkey PRIMARY KEY (id);


--
-- Name: shot_audio_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY shot_audio
    ADD CONSTRAINT shot_audio_pkey PRIMARY KEY (id);


--
-- Name: shot_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY shot
    ADD CONSTRAINT shot_code_key UNIQUE (code);


--
-- Name: shot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY shot
    ADD CONSTRAINT shot_pkey PRIMARY KEY (code);


--
-- Name: storyboard_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY storyboard
    ADD CONSTRAINT storyboard_pkey PRIMARY KEY (id);


--
-- Name: submission_id_bin_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY submission_in_bin
    ADD CONSTRAINT submission_id_bin_id_key UNIQUE (submission_id, bin_id);


--
-- Name: submission_in_bin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY submission_in_bin
    ADD CONSTRAINT submission_in_bin_pkey PRIMARY KEY (id);


--
-- Name: submission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY submission
    ADD CONSTRAINT submission_pkey PRIMARY KEY (id);


--
-- Name: texture_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY texture
    ADD CONSTRAINT texture_pkey PRIMARY KEY (id);


--
-- Name: texture_source_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY texture_source
    ADD CONSTRAINT texture_source_pkey PRIMARY KEY (id);


--
-- Name: plate_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX plate_code_idx ON plate USING btree (code);


--
-- Name: prod_setting_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX prod_setting_name_idx ON prod_setting USING btree ("key");


--
-- Name: render_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX render_code_idx ON render USING btree (code);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer
    ADD CONSTRAINT "$1" FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY composite
    ADD CONSTRAINT "$1" FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY texture
    ADD CONSTRAINT "$1" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY asset
    ADD CONSTRAINT "$1" FOREIGN KEY (asset_type) REFERENCES asset_type(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer_instance
    ADD CONSTRAINT "$1" FOREIGN KEY (layer_id) REFERENCES layer(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer_instance
    ADD CONSTRAINT "$2" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: asset_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT asset_code_fkey FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: episode_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "sequence"
    ADD CONSTRAINT episode_code_fkey FOREIGN KEY (episode_code) REFERENCES episode(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sequence_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cut_sequence
    ADD CONSTRAINT sequence_code_fkey FOREIGN KEY (sequence_code) REFERENCES "sequence"(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: shot_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY storyboard
    ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;



--
-- Name: shot_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY plate
    ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: shot_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cut_sequence
    ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: shot_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY shot_audio
    ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: submission_in_bin_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY submission_in_bin
    ADD CONSTRAINT submission_in_bin_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES bin(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: submission_in_bin_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY submission_in_bin
    ADD CONSTRAINT submission_in_bin_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES submission(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: texture_source_asset_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY texture_source
    ADD CONSTRAINT texture_source_asset_code_fkey FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: pga_forms; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_forms FROM PUBLIC;
REVOKE ALL ON TABLE pga_forms FROM postgres;
GRANT ALL ON TABLE pga_forms TO postgres;
GRANT ALL ON TABLE pga_forms TO PUBLIC;


--
-- Name: pga_layout; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_layout FROM PUBLIC;
REVOKE ALL ON TABLE pga_layout FROM postgres;
GRANT ALL ON TABLE pga_layout TO postgres;
GRANT ALL ON TABLE pga_layout TO PUBLIC;


--
-- Name: pga_queries; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_queries FROM PUBLIC;
REVOKE ALL ON TABLE pga_queries FROM postgres;
GRANT ALL ON TABLE pga_queries TO postgres;
GRANT ALL ON TABLE pga_queries TO PUBLIC;


--
-- Name: pga_reports; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_reports FROM PUBLIC;
REVOKE ALL ON TABLE pga_reports FROM postgres;
GRANT ALL ON TABLE pga_reports TO postgres;
GRANT ALL ON TABLE pga_reports TO PUBLIC;


--
-- Name: pga_schema; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_schema FROM PUBLIC;
REVOKE ALL ON TABLE pga_schema FROM postgres;
GRANT ALL ON TABLE pga_schema TO postgres;
GRANT ALL ON TABLE pga_schema TO PUBLIC;


--
-- Name: pga_scripts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_scripts FROM PUBLIC;
REVOKE ALL ON TABLE pga_scripts FROM postgres;
GRANT ALL ON TABLE pga_scripts TO postgres;
GRANT ALL ON TABLE pga_scripts TO PUBLIC;


--
-- PostgreSQL database dump complete
--

