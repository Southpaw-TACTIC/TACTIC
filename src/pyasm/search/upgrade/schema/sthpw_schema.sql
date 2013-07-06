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

--
-- Name: statinfo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE statinfo AS (
	word text,
	ndoc integer,
	nentry integer
);


ALTER TYPE public.statinfo OWNER TO postgres;

--
-- Name: tokenout; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE tokenout AS (
	tokid integer,
	token text
);


ALTER TYPE public.tokenout OWNER TO postgres;

--
-- Name: tokentype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE tokentype AS (
	tokid integer,
	alias text,
	descr text
);


ALTER TYPE public.tokentype OWNER TO postgres;

--
-- Name: _get_parser_from_curcfg(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _get_parser_from_curcfg() RETURNS text
    AS $$ select prs_name from pg_ts_cfg where oid = show_curcfg() $$
    LANGUAGE sql IMMUTABLE STRICT;


ALTER FUNCTION public._get_parser_from_curcfg() OWNER TO postgres;

--
-- Name: pg_file_length(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pg_file_length(text) RETURNS bigint
    AS $_$SELECT len FROM pg_file_stat($1) AS s(len int8, c timestamp, a timestamp, m timestamp, i bool)$_$
    LANGUAGE sql STRICT;


ALTER FUNCTION public.pg_file_length(text) OWNER TO postgres;

--
-- Name: pg_file_rename(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pg_file_rename(text, text) RETURNS boolean
    AS $_$SELECT pg_file_rename($1, $2, NULL); $_$
    LANGUAGE sql STRICT;


ALTER FUNCTION public.pg_file_rename(text, text) OWNER TO postgres;

--
-- Name: plpgsql_call_handler(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    AS '$libdir/plpgsql', 'plpgsql_call_handler'
    LANGUAGE c;


ALTER FUNCTION public.plpgsql_call_handler() OWNER TO postgres;

--
-- Name: plpgsql_validator(oid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_validator(oid) RETURNS void
    AS '$libdir/plpgsql', 'plpgsql_validator'
    LANGUAGE c;


ALTER FUNCTION public.plpgsql_validator(oid) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: access_rule; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE access_rule (
    id integer NOT NULL,
    project_code character varying(256),
    code character varying(256),
    description text,
    "rule" text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.access_rule OWNER TO postgres;

--
-- Name: access_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE access_rule_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_rule_id_seq OWNER TO postgres;

--
-- Name: access_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE access_rule_id_seq OWNED BY access_rule.id;


--
-- Name: access_rule_in_group; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE access_rule_in_group (
    id integer NOT NULL,
    login_group character varying(256),
    access_rule_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.access_rule_in_group OWNER TO postgres;

--
-- Name: access_rule_in_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE access_rule_in_group_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.access_rule_in_group_id_seq OWNER TO postgres;

--
-- Name: access_rule_in_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE access_rule_in_group_id_seq OWNED BY access_rule_in_group.id;


--
-- Name: annotation; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE annotation (
    id integer NOT NULL,
    xpos integer NOT NULL,
    ypos integer NOT NULL,
    message text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    file_code character varying(30)
);


ALTER TABLE public.annotation OWNER TO postgres;

--
-- Name: annotation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE annotation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.annotation_id_seq OWNER TO postgres;

--
-- Name: annotation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE annotation_id_seq OWNED BY annotation.id;


--
-- Name: clipboard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE clipboard (
    id integer NOT NULL,
    project_code character varying(256),
    "login" character varying(256),
    search_type character varying(256),
    search_id integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    category character varying(256)
);


ALTER TABLE public.clipboard OWNER TO postgres;

--
-- Name: clipboard_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE clipboard_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.clipboard_id_seq OWNER TO postgres;

--
-- Name: clipboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE clipboard_id_seq OWNED BY clipboard.id;


--
-- Name: command; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE command (
    id integer NOT NULL,
    class_name character varying(100) NOT NULL,
    description text,
    notification_code character varying(30) NOT NULL,
    s_status character varying(256)
);


ALTER TABLE public.command OWNER TO postgres;

--
-- Name: command_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE command_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.command_id_seq OWNER TO postgres;

--
-- Name: command_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE command_id_seq OWNED BY command.id;


--
-- Name: command_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE command_log (
    id integer NOT NULL,
    class_name character varying(100) NOT NULL,
    parameters text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.command_log OWNER TO postgres;

--
-- Name: command_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE command_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.command_log_id_seq OWNER TO postgres;

--
-- Name: command_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE command_log_id_seq OWNED BY command_log.id;


--
-- Name: connection; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "connection" (
    id integer NOT NULL,
    context character varying(60),
    project_code character varying(30),
    src_search_type character varying(200),
    src_search_id integer,
    dst_search_type character varying(200),
    dst_search_id integer,
    "login" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public."connection" OWNER TO postgres;

--
-- Name: connection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE connection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.connection_id_seq OWNER TO postgres;

--
-- Name: connection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE connection_id_seq OWNED BY "connection".id;


--
-- Name: debug_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE debug_log (
    id integer NOT NULL,
    category character varying(256),
    "level" character varying(256),
    message text,
    "timestamp" timestamp without time zone DEFAULT now(),
    "login" character varying(256),
    s_status character varying(30)
);


ALTER TABLE public.debug_log OWNER TO postgres;

--
-- Name: debug_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE debug_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.debug_log_id_seq OWNER TO postgres;

--
-- Name: debug_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE debug_log_id_seq OWNED BY debug_log.id;


--
-- Name: exception_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE exception_log (
    id integer NOT NULL,
    "class" character varying(100),
    message text,
    stack_trace text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.exception_log OWNER TO postgres;

--
-- Name: exception_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE exception_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.exception_log_id_seq OWNER TO postgres;

--
-- Name: exception_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE exception_log_id_seq OWNED BY exception_log.id;


--
-- Name: file; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE file (
    id integer NOT NULL,
    file_name character varying(512),
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    st_size bigint,
    file_range text,
    code character varying(30),
    snapshot_code character varying(30),
    project_code character varying(100),
    md5 character varying(32),
    checkin_dir text,
    source_path text,
    relative_dir text,
    "type" character varying(256),
    base_type character varying(256),
    repo_type character varying(256)
);


ALTER TABLE public.file OWNER TO postgres;

--
-- Name: file_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY file
    ADD CONSTRAINT file_code_unique UNIQUE (code);

--
-- Name: file_file_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX file_file_name_idx ON file USING btree (file_name);

--
-- Name: file_access; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE file_access (
    id integer NOT NULL,
    file_code integer NOT NULL,
    "login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.file_access OWNER TO postgres;

--
-- Name: file_access_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE file_access_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.file_access_id_seq OWNER TO postgres;

--
-- Name: file_access_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE file_access_id_seq OWNED BY file_access.id;


--
-- Name: file_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE file_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.file_id_seq OWNER TO postgres;

--
-- Name: file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE file_id_seq OWNED BY file.id;


--
-- Name: group_notification; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE group_notification (
    id integer NOT NULL,
    login_group character varying(100) NOT NULL,
    notification_id integer NOT NULL
);


ALTER TABLE public.group_notification OWNER TO postgres;

--
-- Name: group_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE group_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.group_notification_id_seq OWNER TO postgres;

--
-- Name: group_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE group_notification_id_seq OWNED BY group_notification.id;


--
-- Name: login; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "login" (
    id integer NOT NULL,
    code character varying(512),
    "login" character varying(100) NOT NULL,
    "password" character varying(255),
    login_groups text,
    first_name character varying(100),
    last_name character varying(100),
    email character varying(200),
    phone_number character varying(32),
    department character varying(256),
    namespace character varying(255),
    snapshot text,
    s_status character varying(30),
    project_code text,
    license_type character varying(256)
);


ALTER TABLE public."login" OWNER TO postgres;

--
-- Name: login_group; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE login_group (
    id integer NOT NULL,
    code character varying(256),
    login_group character varying(100) NOT NULL,
    sub_groups text,
    access_rules text,
    redirect_url text,
    namespace character varying(255),
    description text,
    project_code text,
    access_level character varying(32),
    s_status character varying(256)
);


ALTER TABLE public.login_group OWNER TO postgres;

--
-- Name: login_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE login_group_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.login_group_id_seq OWNER TO postgres;

--
-- Name: login_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE login_group_id_seq OWNED BY login_group.id;


--
-- Name: login_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE login_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.login_id_seq OWNER TO postgres;

--
-- Name: login_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE login_id_seq OWNED BY "login".id;


--
-- Name: login_in_group; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE login_in_group (
    id integer NOT NULL,
    code character varying(256),
    "login" character varying(100) NOT NULL,
    login_group character varying(100) NOT NULL
);


ALTER TABLE public.login_in_group OWNER TO postgres;

--
-- Name: login_in_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE login_in_group_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.login_in_group_id_seq OWNER TO postgres;

--
-- Name: login_in_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE login_in_group_id_seq OWNED BY login_in_group.id;


--
-- Name: milestone; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE milestone (
    id integer NOT NULL,
    code character varying(200),
    project_code character varying(30),
    description text,
    due_date timestamp without time zone
);


ALTER TABLE public.milestone OWNER TO postgres;

--
-- Name: milestone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE milestone_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.milestone_id_seq OWNER TO postgres;

--
-- Name: milestone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE milestone_id_seq OWNED BY milestone.id;


--
-- Name: note; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE note (
    id integer NOT NULL,
    project_code character varying(30),
    search_type character varying(200),
    search_id integer,
    "login" character varying(30),
    context character varying(60),
    "timestamp" timestamp without time zone DEFAULT now(),
    note text,
    title character varying(1024),
    parent_id bigint,
    status character varying(256),
    label character varying(256),
    process character varying(60),
    "sort_order" integer,
    code character varying(256),
    "access" character varying(256)
);


ALTER TABLE public.note OWNER TO postgres;

--
-- Name: note_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE note_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.note_id_seq OWNER TO postgres;

--
-- Name: note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE note_id_seq OWNED BY note.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE notification (
    id integer NOT NULL,
    code character varying(30),
    event character varying(256),
    listen_event character varying(256),
    data text,
    description text,
    process varchar(256),
    "type" character varying(30) NOT NULL,
    search_type character varying(100),
    project_code character varying(30),
    rules text,
    subject text,
    message text,
    email_handler_cls character varying(200),
    mail_to text,
    mail_cc text,
    mail_bcc text,
    s_status character varying(30)
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE notification_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.notification_id_seq OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE notification_id_seq OWNED BY notification.id;


--
-- Name: notification_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE notification_log (
    id integer NOT NULL,
    project_code character varying(256),
    "login" character varying(256),
    command_cls character varying(256),
    subject text,
    message text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.notification_log OWNER TO postgres;

--
-- Name: notification_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE notification_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.notification_log_id_seq OWNER TO postgres;

--
-- Name: notification_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE notification_log_id_seq OWNED BY notification_log.id;


--
-- Name: notification_login; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE notification_login (
    id integer NOT NULL,
    notification_log_id integer,
    "login" character varying(256),
    "type" character varying(256),
    project_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.notification_login OWNER TO postgres;

--
-- Name: notification_login_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE notification_login_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.notification_login_id_seq OWNER TO postgres;

--
-- Name: notification_login_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE notification_login_id_seq OWNED BY notification_login.id;


SET default_with_oids = true;

--
-- Name: pg_ts_cfg; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pg_ts_cfg (
    ts_name text NOT NULL,
    prs_name text NOT NULL,
    locale text
);


ALTER TABLE public.pg_ts_cfg OWNER TO postgres;

--
-- Name: pg_ts_cfgmap; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pg_ts_cfgmap (
    ts_name text NOT NULL,
    tok_alias text NOT NULL,
    dict_name text[]
);


ALTER TABLE public.pg_ts_cfgmap OWNER TO postgres;

--
-- Name: pg_ts_dict; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pg_ts_dict (
    dict_name text NOT NULL,
    dict_init regprocedure,
    dict_initoption text,
    dict_lexize regprocedure NOT NULL,
    dict_comment text
);


ALTER TABLE public.pg_ts_dict OWNER TO postgres;

--
-- Name: pg_ts_parser; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pg_ts_parser (
    prs_name text NOT NULL,
    prs_start regprocedure NOT NULL,
    prs_nexttoken regprocedure NOT NULL,
    prs_end regprocedure NOT NULL,
    prs_headline regprocedure NOT NULL,
    prs_lextype regprocedure NOT NULL,
    prs_comment text
);


ALTER TABLE public.pg_ts_parser OWNER TO postgres;

--
-- Name: pga_diagrams; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_diagrams (
    diagramname character varying(64) NOT NULL,
    diagramtables text,
    diagramlinks text
);


ALTER TABLE public.pga_diagrams OWNER TO postgres;

--
-- Name: pga_forms; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_forms (
    formname character varying(64) NOT NULL,
    formsource text
);


ALTER TABLE public.pga_forms OWNER TO postgres;

--
-- Name: pga_graphs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_graphs (
    graphname character varying(64) NOT NULL,
    graphsource text,
    graphcode text
);


ALTER TABLE public.pga_graphs OWNER TO postgres;

--
-- Name: pga_images; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_images (
    imagename character varying(64) NOT NULL,
    imagesource text
);


ALTER TABLE public.pga_images OWNER TO postgres;

SET default_with_oids = false;

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

SET default_with_oids = true;

--
-- Name: pga_queries; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_queries (
    queryname character varying(64) NOT NULL,
    querytype character(1),
    querycommand text,
    querytables text,
    querylinks text,
    queryresults text,
    querycomments text
);


ALTER TABLE public.pga_queries OWNER TO postgres;

SET default_with_oids = false;

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

SET default_with_oids = true;

--
-- Name: pga_scripts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_scripts (
    scriptname character varying(64) NOT NULL,
    scriptsource text
);


ALTER TABLE public.pga_scripts OWNER TO postgres;

SET default_with_oids = false;

--
-- Name: pipeline; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pipeline (
    id integer NOT NULL,
    code character varying(128) NOT NULL,
    pipeline text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    search_type character varying(100),
    project_code character varying(30),
    description text,
    color varchar(256),
    autocreate_tasks boolean,
    s_status character varying(30)
);


ALTER TABLE public.pipeline OWNER TO postgres;

--
-- Name: pipeline_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pipeline_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.pipeline_id_seq OWNER TO postgres;

--
-- Name: pipeline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pipeline_id_seq OWNED BY pipeline.id;


--
-- Name: pref_list; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pref_list (
    id integer NOT NULL,
    "key" character varying(256),
    description text,
    options text,
    "type" character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    title text
);


ALTER TABLE public.pref_list OWNER TO postgres;

--
-- Name: pref_list_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pref_list_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.pref_list_id_seq OWNER TO postgres;

--
-- Name: pref_list_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pref_list_id_seq OWNED BY pref_list.id;


--
-- Name: pref_setting; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pref_setting (
    id integer NOT NULL,
    project_code character varying(256),
    "login" character varying(256),
    "key" character varying(256),
    value text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.pref_setting OWNER TO postgres;

--
-- Name: pref_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pref_setting_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.pref_setting_id_seq OWNER TO postgres;

--
-- Name: pref_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pref_setting_id_seq OWNED BY pref_setting.id;


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
    START WITH 1
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
-- Name: project; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE project (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    title character varying(100),
    sobject_mapping_cls character varying(100),
    dir_naming_cls character varying(200),
    code_naming_cls character varying(200),
    pipeline character varying(30),
    snapshot text,
    "type" character varying(256),
    last_db_update timestamp without time zone,
    description text,
    initials character varying(30),
    file_naming_cls character varying(200),
    reg_hours numeric,
    node_naming_cls character varying(200),
    s_status character varying(30),
    status character varying(256),
    last_version_update character varying(256)
);


ALTER TABLE public.project OWNER TO postgres;

--
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE project_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.project_id_seq OWNER TO postgres;

--
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE project_id_seq OWNED BY project.id;


--
-- Name: project_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE project_type (
    id integer NOT NULL,
    code character varying(256),
    dir_naming_cls character varying(200),
    file_naming_cls character varying(200),
    code_naming_cls character varying(200),
    node_naming_cls character varying(200),
    sobject_mapping_cls character varying(200),
    s_status character varying(32),
    "type" character varying(100) NOT NULL,
    repo_handler_cls character varying(200)
);


ALTER TABLE public.project_type OWNER TO postgres;

--
-- Name: project_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE project_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.project_type_id_seq OWNER TO postgres;

--
-- Name: project_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE project_type_id_seq OWNED BY project_type.id;


--
-- Name: queue; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE queue (
    id integer NOT NULL,
    queue character varying(30) NOT NULL,
    priority character varying(10) NOT NULL,
    description text,
    state character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    "login" character varying(30) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    command character varying(200) NOT NULL,
    serialized text NOT NULL,
    s_status character varying(30),
    project_code character varying(100),
    search_id integer,
    search_type character varying(100),
    dispatcher_id integer,
    policy_code character varying(30),
    host character varying(256)
);


ALTER TABLE public.queue OWNER TO postgres;

--
-- Name: queue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.queue_id_seq OWNER TO postgres;

--
-- Name: queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE queue_id_seq OWNED BY queue.id;


--
-- Name: remote_repo; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE remote_repo (
    id integer NOT NULL,
    code character varying(30),
    ip_address character varying(30),
    ip_mask character varying(30),
    repo_base_dir character varying(200),
    sandbox_base_dir character varying(200),
    "login" character varying(100)
);


ALTER TABLE public.remote_repo OWNER TO postgres;

--
-- Name: remote_repo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE remote_repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.remote_repo_id_seq OWNER TO postgres;

--
-- Name: remote_repo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE remote_repo_id_seq OWNED BY remote_repo.id;


--
-- Name: repo; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE repo (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    description character varying(200) NOT NULL,
    "handler" character varying(100) NOT NULL,
    web_dir text NOT NULL,
    lib_dir text NOT NULL
);


ALTER TABLE public.repo OWNER TO postgres;

--
-- Name: repo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.repo_id_seq OWNER TO postgres;

--
-- Name: repo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE repo_id_seq OWNED BY repo.id;


--
-- Name: retire_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE retire_log (
    id integer NOT NULL,
    search_type character varying(100),
    search_id character varying(100),
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.retire_log OWNER TO postgres;

--
-- Name: retire_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE retire_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.retire_log_id_seq OWNER TO postgres;

--
-- Name: retire_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE retire_log_id_seq OWNED BY retire_log.id;


--
-- Name: schema; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "schema" (
    id integer NOT NULL,
    code character varying(256),
    description text,
    "schema" text,
    "timestamp" timestamp without time zone DEFAULT now(),
    "login" character varying(256),
    s_status character varying(30)
);


ALTER TABLE public."schema" OWNER TO postgres;

--
-- Name: schema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schema_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.schema_id_seq OWNER TO postgres;

--
-- Name: schema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schema_id_seq OWNED BY "schema".id;


--
-- Name: search_object; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE search_object (
    id integer NOT NULL,
    code character varying(256),
    search_type character varying(100) NOT NULL,
    namespace character varying(200) NOT NULL,
    description text,
    "database" character varying(100) NOT NULL,
    table_name character varying(100) NOT NULL,
    class_name character varying(100) NOT NULL,
    title character varying(100),
    "schema" character varying(100)
);


ALTER TABLE public.search_object OWNER TO postgres;

--
-- Name: search_object_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE search_object_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.search_object_id_seq OWNER TO postgres;

--
-- Name: search_object_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE search_object_id_seq OWNED BY search_object.id;


--
-- Name: snapshot; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE snapshot (
    id integer NOT NULL,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    column_name character varying(100) NOT NULL,
    snapshot text NOT NULL,
    description text,
    process varchar(256),
    "login" character varying(100) NOT NULL,
    "lock_login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    lock_date timestamp,
    context character varying(256),
    version integer,
    s_status character varying(30),
    snapshot_type character varying(30),
    code character varying(30),
    repo character varying(30),
    is_current boolean,
    label character varying(100),
    revision smallint,
    level_type character varying(256),
    level_id integer,
    metadata text,
    is_latest boolean,
    status character varying(256),
    project_code character varying(256),
    search_code character varying(256),
    is_synced boolean
);


ALTER TABLE public.snapshot OWNER TO postgres;

--
-- Name: snapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE snapshot_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.snapshot_id_seq OWNER TO postgres;

--
-- Name: snapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE snapshot_id_seq OWNED BY snapshot.id;



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
    snapshot_flavor text,
    relfile text
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
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE snapshot_type ALTER COLUMN id SET DEFAULT nextval('snapshot_type_id_seq'::regclass);


--
-- Name: snapshot_type_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY snapshot_type
    ADD CONSTRAINT snapshot_type_code_unique UNIQUE (code);



--
-- Name: sobject_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sobject_log (
    id integer NOT NULL,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    data text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    transaction_log_id integer
);


ALTER TABLE public.sobject_log OWNER TO postgres;

--
-- Name: sobject_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE sobject_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.sobject_log_id_seq OWNER TO postgres;

--
-- Name: sobject_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE sobject_log_id_seq OWNED BY sobject_log.id;


--
-- Name: special_day; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE special_day (
    id integer NOT NULL,
    week smallint,
    mon real,
    tue real,
    wed real,
    thu real,
    fri real,
    sat real,
    sun real,
    "year" integer,
    "login" character varying(100),
    description text,
    "type" character varying(100),
    project_code character varying(30)
);


ALTER TABLE public.special_day OWNER TO postgres;

--
-- Name: special_day_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE special_day_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.special_day_id_seq OWNER TO postgres;

--
-- Name: special_day_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE special_day_id_seq OWNED BY special_day.id;


--
-- Name: status_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE status_log (
    id integer NOT NULL,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    status text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    to_status character varying(256),
    from_status character varying(256),
    project_code character varying(256)
);


ALTER TABLE public.status_log OWNER TO postgres;

--
-- Name: status_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE status_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.status_log_id_seq OWNER TO postgres;

--
-- Name: status_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE status_log_id_seq OWNED BY status_log.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE task (
    id integer NOT NULL,
    assigned character varying(100),
    description text,
    status text,
    discussion text,
    bid_start_date timestamp without time zone,
    bid_end_date timestamp without time zone,
    bid_duration double precision,
    actual_start_date timestamp without time zone,
    actual_end_date timestamp without time zone,
    search_type character varying(100),
    search_id integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    priority smallint,
    process character varying(256),
    context character varying(256),
    milestone_code character varying(200),
    pipeline_code character varying(256),
    parent_id integer,
    sort_order smallint,
    depend_id integer,
    project_code character varying(100),
    supervisor character varying(100),
    code character varying(256),
    login character varying(256),
    completion float
);


ALTER TABLE public.task OWNER TO postgres;

--
-- Name: task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE task_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.task_id_seq OWNER TO postgres;

--
-- Name: task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE task_id_seq OWNED BY task.id;


--
-- Name: ticket; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE ticket (
    id integer NOT NULL,
    ticket character varying(100) NOT NULL,
    "login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    expiry timestamp without time zone
);


ALTER TABLE public.ticket OWNER TO postgres;

--
-- Name: ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE ticket_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.ticket_id_seq OWNER TO postgres;

--
-- Name: ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE ticket_id_seq OWNED BY ticket.id;


--
-- Name: timecard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE timecard (
    id integer NOT NULL,
    search_type character varying(100),
    search_id integer,
    week smallint,
    mon real,
    tue real,
    wed real,
    thu real,
    fri real,
    sat real,
    sun real,
    "login" character varying(100),
    project_code character varying(30),
    "year" integer,
    description text
);


ALTER TABLE public.timecard OWNER TO postgres;

--
-- Name: timecard_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE timecard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.timecard_id_seq OWNER TO postgres;

--
-- Name: timecard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE timecard_id_seq OWNED BY timecard.id;


--
-- Name: transaction_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE transaction_log (
    id integer NOT NULL,
    "transaction" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    description text,
    command character varying(100),
    title text,
    "type" character varying(30),
    namespace character varying(100),
    code character varying(256),
    ticket character varying(256),
    state character varying(256),
    server_code character varying(256)
);


ALTER TABLE public.transaction_log OWNER TO postgres;

--
-- Name: transaction_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE transaction_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.transaction_log_id_seq OWNER TO postgres;

--
-- Name: transaction_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE transaction_log_id_seq OWNED BY transaction_log.id;


--
-- Name: transaction_state; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE transaction_state (
    id integer NOT NULL,
    ticket character varying(100),
    "timestamp" timestamp without time zone DEFAULT now(),
    data text
);


ALTER TABLE public.transaction_state OWNER TO postgres;

--
-- Name: transaction_state_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE transaction_state_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.transaction_state_id_seq OWNER TO postgres;

--
-- Name: transaction_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE transaction_state_id_seq OWNED BY transaction_state.id;


--
-- Name: translation; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE translation (
    id integer NOT NULL,
    "language" character varying(32),
    msgid text,
    msgstr text,
    line text,
    "login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.translation OWNER TO postgres;

--
-- Name: translation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE translation_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.translation_id_seq OWNER TO postgres;

--
-- Name: translation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE translation_id_seq OWNED BY translation.id;


--
-- Name: trigger; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "trigger" (
    id integer NOT NULL,
    class_name character varying(256),
    script_path character varying(256),
    description text,
    event character varying(256),
    mode character varying(256),
    project_code character varying(256),
    process character varying(256),
    s_status character varying(256)
);


ALTER TABLE public."trigger" OWNER TO postgres;

--
-- Name: trigger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE trigger_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.trigger_id_seq OWNER TO postgres;

--
-- Name: trigger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE trigger_id_seq OWNED BY "trigger".id;


--
-- Name: trigger_in_command; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE trigger_in_command (
    id integer NOT NULL,
    command_code character varying(100) NOT NULL,
    trigger_code character varying(100) NOT NULL
);


ALTER TABLE public.trigger_in_command OWNER TO postgres;

--
-- Name: trigger_in_command_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE trigger_in_command_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.trigger_in_command_id_seq OWNER TO postgres;

--
-- Name: trigger_in_command_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE trigger_in_command_id_seq OWNED BY trigger_in_command.id;


--
-- Name: wdg_settings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE wdg_settings (
    id integer NOT NULL,
    "key" character varying(255) NOT NULL,
    "login" character varying(100) NOT NULL,
    data text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    project_code character varying(30)
);


ALTER TABLE public.wdg_settings OWNER TO postgres;

--
-- Name: wdg_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE wdg_settings_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.wdg_settings_id_seq OWNER TO postgres;

--
-- Name: wdg_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE wdg_settings_id_seq OWNED BY wdg_settings.id;

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
    s_status character varying(32),
    project_code character varying(256)
);


ALTER TABLE public.widget_config OWNER TO postgres;

--
-- Name: widget_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE widget_config_id_seq
    START WITH 1
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

ALTER TABLE widget_config ALTER COLUMN id SET DEFAULT nextval('widget_config_id_seq'::regclass);


--
-- Name: widget_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY widget_config
    ADD CONSTRAINT widget_config_pkey PRIMARY KEY (id);


--
-- Name: widget_config_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX widget_config_code_idx ON widget_config USING btree (code);


--
-- Name: widget_extend; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE widget_extend (
    id integer NOT NULL,
    "key" character varying(256),
    "type" character varying(256),
    data text,
    project_code character varying(256),
    "login" character varying(32),
    "timestamp" timestamp without time zone,
    s_status character varying(32),
    description text
);


ALTER TABLE public.widget_extend OWNER TO postgres;

--
-- Name: widget_extend_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE widget_extend_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.widget_extend_id_seq OWNER TO postgres;

--
-- Name: widget_extend_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE widget_extend_id_seq OWNED BY widget_extend.id;


--
-- Name: cache; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "cache" (
    id integer NOT NULL,
    "key" character varying(256),
    mtime timestamp without time zone
);


ALTER TABLE public."cache" OWNER TO postgres;

--
-- Name: cache_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.cache_id_seq OWNER TO postgres;

--
-- Name: cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE cache_id_seq OWNED BY "cache".id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "cache" ALTER COLUMN id SET DEFAULT nextval('cache_id_seq'::regclass);


--
-- Name: cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "cache"
    ADD CONSTRAINT cache_pkey PRIMARY KEY (id);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE access_rule ALTER COLUMN id SET DEFAULT nextval('access_rule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE access_rule_in_group ALTER COLUMN id SET DEFAULT nextval('access_rule_in_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE annotation ALTER COLUMN id SET DEFAULT nextval('annotation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE clipboard ALTER COLUMN id SET DEFAULT nextval('clipboard_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE command ALTER COLUMN id SET DEFAULT nextval('command_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE command_log ALTER COLUMN id SET DEFAULT nextval('command_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "connection" ALTER COLUMN id SET DEFAULT nextval('connection_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE debug_log ALTER COLUMN id SET DEFAULT nextval('debug_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE exception_log ALTER COLUMN id SET DEFAULT nextval('exception_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE file ALTER COLUMN id SET DEFAULT nextval('file_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE file_access ALTER COLUMN id SET DEFAULT nextval('file_access_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE group_notification ALTER COLUMN id SET DEFAULT nextval('group_notification_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "login" ALTER COLUMN id SET DEFAULT nextval('login_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE login_group ALTER COLUMN id SET DEFAULT nextval('login_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE login_in_group ALTER COLUMN id SET DEFAULT nextval('login_in_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE milestone ALTER COLUMN id SET DEFAULT nextval('milestone_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE note ALTER COLUMN id SET DEFAULT nextval('note_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE notification ALTER COLUMN id SET DEFAULT nextval('notification_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE notification_log ALTER COLUMN id SET DEFAULT nextval('notification_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE notification_login ALTER COLUMN id SET DEFAULT nextval('notification_login_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE pipeline ALTER COLUMN id SET DEFAULT nextval('pipeline_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE pref_list ALTER COLUMN id SET DEFAULT nextval('pref_list_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE pref_setting ALTER COLUMN id SET DEFAULT nextval('pref_setting_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE prod_setting ALTER COLUMN id SET DEFAULT nextval('prod_setting_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE project ALTER COLUMN id SET DEFAULT nextval('project_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE project_type ALTER COLUMN id SET DEFAULT nextval('project_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE queue ALTER COLUMN id SET DEFAULT nextval('queue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE remote_repo ALTER COLUMN id SET DEFAULT nextval('remote_repo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE repo ALTER COLUMN id SET DEFAULT nextval('repo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE retire_log ALTER COLUMN id SET DEFAULT nextval('retire_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "schema" ALTER COLUMN id SET DEFAULT nextval('schema_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE search_object ALTER COLUMN id SET DEFAULT nextval('search_object_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE snapshot ALTER COLUMN id SET DEFAULT nextval('snapshot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE snapshot_type ALTER COLUMN id SET DEFAULT nextval('snapshot_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE sobject_log ALTER COLUMN id SET DEFAULT nextval('sobject_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE special_day ALTER COLUMN id SET DEFAULT nextval('special_day_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE status_log ALTER COLUMN id SET DEFAULT nextval('status_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE task ALTER COLUMN id SET DEFAULT nextval('task_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ticket ALTER COLUMN id SET DEFAULT nextval('ticket_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE timecard ALTER COLUMN id SET DEFAULT nextval('timecard_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE transaction_log ALTER COLUMN id SET DEFAULT nextval('transaction_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE transaction_state ALTER COLUMN id SET DEFAULT nextval('transaction_state_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE translation ALTER COLUMN id SET DEFAULT nextval('translation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE "trigger" ALTER COLUMN id SET DEFAULT nextval('trigger_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE trigger_in_command ALTER COLUMN id SET DEFAULT nextval('trigger_in_command_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE wdg_settings ALTER COLUMN id SET DEFAULT nextval('wdg_settings_id_seq'::regclass);




--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE widget_extend ALTER COLUMN id SET DEFAULT nextval('widget_extend_id_seq'::regclass);


--
-- Name: access_rule_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY access_rule
    ADD CONSTRAINT access_rule_code_key UNIQUE (code);


--
-- Name: access_rule_in_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY access_rule_in_group
    ADD CONSTRAINT access_rule_in_group_pkey PRIMARY KEY (id);


--
-- Name: access_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY access_rule
    ADD CONSTRAINT access_rule_pkey PRIMARY KEY (id);


--
-- Name: annotation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY annotation
    ADD CONSTRAINT annotation_pkey PRIMARY KEY (id);


--
-- Name: clipboard_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY clipboard
    ADD CONSTRAINT clipboard_pkey PRIMARY KEY (id);


--
-- Name: code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY project_type
    ADD CONSTRAINT code_key UNIQUE (code);


--
-- Name: command_class_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY command
    ADD CONSTRAINT command_class_name_key UNIQUE (class_name);


--
-- Name: command_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY command_log
    ADD CONSTRAINT command_log_pkey PRIMARY KEY (id);


--
-- Name: command_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY command
    ADD CONSTRAINT command_pkey PRIMARY KEY (id);


--
-- Name: connection_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "connection"
    ADD CONSTRAINT connection_pkey PRIMARY KEY (id);


--
-- Name: exception_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY exception_log
    ADD CONSTRAINT exception_log_pkey PRIMARY KEY (id);


--
-- Name: file_access_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY file_access
    ADD CONSTRAINT file_access_pkey PRIMARY KEY (id);


--
-- Name: file_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY file
    ADD CONSTRAINT file_pkey PRIMARY KEY (id);


--
-- Name: group_notification_login_group_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY group_notification
    ADD CONSTRAINT group_notification_login_group_code_key UNIQUE (login_group, notification_id);


--
-- Name: group_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY group_notification
    ADD CONSTRAINT group_notification_pkey PRIMARY KEY (id);


--
-- Name: login_group_login_group_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY login_group
    ADD CONSTRAINT login_group_login_group_key UNIQUE (login_group);


--
-- Name: login_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY login_group
    ADD CONSTRAINT login_group_pkey PRIMARY KEY (id);


--
-- Name: login_in_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY login_in_group
    ADD CONSTRAINT login_in_group_pkey PRIMARY KEY (id);


--
-- Name: login_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "login"
    ADD CONSTRAINT login_login_key UNIQUE ("login");


--
-- Name: login_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "login"
    ADD CONSTRAINT login_pkey PRIMARY KEY (id);


--
-- Name: milestone_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY milestone
    ADD CONSTRAINT milestone_pkey PRIMARY KEY (id);


--
-- Name: milestone_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY milestone
    ADD CONSTRAINT milestone_unique UNIQUE (code);


--
-- Name: note_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY note
    ADD CONSTRAINT note_pkey PRIMARY KEY (id);


--
-- Name: notification_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notification_log
    ADD CONSTRAINT notification_log_pkey PRIMARY KEY (id);


--
-- Name: notification_login_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notification_login
    ADD CONSTRAINT notification_login_pkey PRIMARY KEY (id);


--
-- Name: notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: pg_ts_cfg_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pg_ts_cfg
    ADD CONSTRAINT pg_ts_cfg_pkey PRIMARY KEY (ts_name);


--
-- Name: pg_ts_cfgmap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pg_ts_cfgmap
    ADD CONSTRAINT pg_ts_cfgmap_pkey PRIMARY KEY (ts_name, tok_alias);


--
-- Name: pg_ts_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pg_ts_dict
    ADD CONSTRAINT pg_ts_dict_pkey PRIMARY KEY (dict_name);


--
-- Name: pg_ts_parser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pg_ts_parser
    ADD CONSTRAINT pg_ts_parser_pkey PRIMARY KEY (prs_name);


--
-- Name: pga_diagrams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_diagrams
    ADD CONSTRAINT pga_diagrams_pkey PRIMARY KEY (diagramname);


--
-- Name: pga_forms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_forms
    ADD CONSTRAINT pga_forms_pkey PRIMARY KEY (formname);


--
-- Name: pga_graphs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_graphs
    ADD CONSTRAINT pga_graphs_pkey PRIMARY KEY (graphname);


--
-- Name: pga_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_images
    ADD CONSTRAINT pga_images_pkey PRIMARY KEY (imagename);


--
-- Name: pga_queries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_queries
    ADD CONSTRAINT pga_queries_pkey PRIMARY KEY (queryname);


--
-- Name: pga_scripts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_scripts
    ADD CONSTRAINT pga_scripts_pkey PRIMARY KEY (scriptname);


--
-- Name: pipeline_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pipeline
    ADD CONSTRAINT pipeline_name_key UNIQUE (code);


--
-- Name: pipeline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pipeline
    ADD CONSTRAINT pipeline_pkey PRIMARY KEY (id);


--
-- Name: pref_list_key_idx; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pref_list
    ADD CONSTRAINT pref_list_key_idx UNIQUE ("key");


--
-- Name: pref_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pref_list
    ADD CONSTRAINT pref_list_pkey PRIMARY KEY (id);


--
-- Name: pref_setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pref_setting
    ADD CONSTRAINT pref_setting_pkey PRIMARY KEY (id);


--
-- Name: project_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY project
    ADD CONSTRAINT project_code_key UNIQUE (code);


--
-- Name: project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- Name: project_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY project_type
    ADD CONSTRAINT project_type_pkey PRIMARY KEY (id);


--
-- Name: queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY queue
    ADD CONSTRAINT queue_pkey PRIMARY KEY (id);


--
-- Name: remote_repo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY remote_repo
    ADD CONSTRAINT remote_repo_pkey PRIMARY KEY (id);


--
-- Name: repo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repo
    ADD CONSTRAINT repo_pkey PRIMARY KEY (id);


--
-- Name: retire_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY retire_log
    ADD CONSTRAINT retire_log_pkey PRIMARY KEY (id);


--
-- Name: schema_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "schema"
    ADD CONSTRAINT schema_code_unique UNIQUE (code);


--
-- Name: schema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "schema"
    ADD CONSTRAINT schema_pkey PRIMARY KEY (id);


--
-- Name: search_object_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY search_object
    ADD CONSTRAINT search_object_pkey PRIMARY KEY (id);


--
-- Name: snapshot_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY snapshot
    ADD CONSTRAINT snapshot_code_key UNIQUE (code);


--
-- Name: snapshot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY snapshot
    ADD CONSTRAINT snapshot_pkey PRIMARY KEY (id);


--
-- Name: snapshot_type_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY snapshot_type
    ADD CONSTRAINT snapshot_type_code_unique UNIQUE (code);




--
-- Name: sobject_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sobject_log
    ADD CONSTRAINT sobject_log_pkey PRIMARY KEY (id);


--
-- Name: special_day_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY special_day
    ADD CONSTRAINT special_day_pkey PRIMARY KEY (id);


--
-- Name: status_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY status_log
    ADD CONSTRAINT status_log_pkey PRIMARY KEY (id);


--
-- Name: task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);

--
-- Name: ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id);

--
-- Name: ticket_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY ticket
    ADD CONSTRAINT ticket_unique UNIQUE (ticket);


--
-- Name: timecard_general_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY timecard
    ADD CONSTRAINT timecard_general_unique UNIQUE (description, week, "year", project_code, "login");


--
-- Name: timecard_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY timecard
    ADD CONSTRAINT timecard_pkey PRIMARY KEY (id);


--
-- Name: timecard_task_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY timecard
    ADD CONSTRAINT timecard_task_unique UNIQUE (search_type, search_id, week, "year", project_code, "login");


--
-- Name: transaction_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY transaction_log
    ADD CONSTRAINT transaction_log_pkey PRIMARY KEY (id);


--
-- Name: translation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY translation
    ADD CONSTRAINT translation_pkey PRIMARY KEY (id);



--
-- Name: trigger_class_name_event_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "trigger"
    ADD CONSTRAINT trigger_class_name_event_unique UNIQUE (class_name, event);

--
-- Name: trigger_in_command_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY trigger_in_command
    ADD CONSTRAINT trigger_in_command_pkey PRIMARY KEY (id);


--
-- Name: trigger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "trigger"
    ADD CONSTRAINT trigger_pkey PRIMARY KEY (id);


--
-- Name: wdg_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY wdg_settings
    ADD CONSTRAINT wdg_settings_pkey PRIMARY KEY (id);


--
-- Name: wdg_settings_unique; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY wdg_settings
    ADD CONSTRAINT wdg_settings_unique UNIQUE ("key", "login", project_code);


--
-- Name: login_in_group_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX login_in_group_idx ON login_in_group USING btree ("login", login_group);

--
-- Name: note_search_type_search_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX note_search_type_search_id_idx ON note USING btree (search_type, search_id);



--
-- Name: snapshot_project_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX snapshot_project_code_idx ON snapshot USING btree (project_code);


--
-- Name: snapshot_search_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX snapshot_search_code_idx ON snapshot USING btree (search_code);

--
-- Name: snapshot_search_type_search_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX snapshot_search_type_search_id_idx ON snapshot USING btree (search_type, search_id);


--
-- Name: queue_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX queue_idx ON queue USING btree (queue, state);


--
-- Name: search_object_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX search_object_idx ON search_object USING btree (search_type);

--
-- Name: task_process_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX task_process_idx ON task USING btree (process);

--
-- Name: task_search_type_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX task_search_type_idx ON task USING btree (search_type);

--
-- Name: task_search_type_search_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX task_search_type_search_id_idx ON task USING btree (search_type, search_id);

--
-- Name: task_status_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX task_status_idx ON task USING btree (status);

--
-- Name: timecard_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX timecard_idx ON timecard USING btree (week, "login", project_code);


--
-- Name: transaction_log_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX transaction_log_idx ON transaction_log USING btree ("timestamp");


--
-- Name: transaction_log_idx2; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX transaction_log_idx2 ON transaction_log USING btree ("login", namespace, "type");


--
-- Name: access_rule_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY access_rule_in_group
    ADD CONSTRAINT access_rule_fkey1 FOREIGN KEY (login_group) REFERENCES login_group(login_group) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: access_rule_fkey2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY access_rule_in_group
    ADD CONSTRAINT access_rule_fkey2 FOREIGN KEY (access_rule_code) REFERENCES access_rule(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_notification_login_group_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY group_notification
    ADD CONSTRAINT group_notification_login_group_fkey FOREIGN KEY (login_group) REFERENCES login_group(login_group) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_notification_notification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY group_notification
    ADD CONSTRAINT group_notification_notification_id_fkey FOREIGN KEY (notification_id) REFERENCES notification(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: login_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY remote_repo
    ADD CONSTRAINT login_fkey FOREIGN KEY ("login") REFERENCES "login"("login") ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: login_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY timecard
    ADD CONSTRAINT login_foreign FOREIGN KEY ("login") REFERENCES "login"("login") ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: milestone_code_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task
    ADD CONSTRAINT milestone_code_foreign FOREIGN KEY (milestone_code) REFERENCES milestone(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notification_search_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_search_type_fkey FOREIGN KEY (search_type) REFERENCES search_object(search_type) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pipeline_code_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task
    ADD CONSTRAINT pipeline_code_foreign FOREIGN KEY (pipeline_code) REFERENCES pipeline(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pipeline_search_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pipeline
    ADD CONSTRAINT pipeline_search_type_fkey FOREIGN KEY (search_type) REFERENCES search_object(search_type) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pref_setting_key_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pref_setting
    ADD CONSTRAINT pref_setting_key_fkey FOREIGN KEY ("key") REFERENCES pref_list("key") ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pref_setting_login_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

-- ALTER TABLE ONLY pref_setting
--    ADD CONSTRAINT pref_setting_login_fkey FOREIGN KEY ("login") REFERENCES "login"("login") ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY file
    ADD CONSTRAINT project_code_fkey FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY queue
    ADD CONSTRAINT project_code_fkey FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY task
    ADD CONSTRAINT project_code_fkey FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_code_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY timecard
    ADD CONSTRAINT project_code_foreign FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;



--
-- Name: project_code_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY special_day
    ADD CONSTRAINT project_code_foreign FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: transaction_log_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY sobject_log
    ADD CONSTRAINT transaction_log_fkey FOREIGN KEY (transaction_log_id) REFERENCES transaction_log(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: trigger_in_command_command_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY trigger_in_command
    ADD CONSTRAINT trigger_in_command_command_code_fkey FOREIGN KEY (command_code) REFERENCES command(class_name) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: trigger_in_command_trigger_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY trigger_in_command
    ADD CONSTRAINT trigger_in_command_trigger_code_fkey FOREIGN KEY (trigger_code) REFERENCES "trigger"(class_name) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wdg_settings_login_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

-- ALTER TABLE ONLY wdg_settings
--    ADD CONSTRAINT wdg_settings_login_fkey FOREIGN KEY ("login") REFERENCES "login"("login") ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wdg_settings_project_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

--ALTER TABLE ONLY wdg_settings
--    ADD CONSTRAINT wdg_settings_project_code_fkey FOREIGN KEY (project_code) REFERENCES project(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: work_hour; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE work_hour (
    id integer NOT NULL,
    code character varying(256),
    project_code character varying(256),
    description text,
    category character varying(256),
    process character varying(256),
    "login" character varying(256),
    "day" timestamp without time zone,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    straight_time double precision,
    over_time double precision,
    search_type character varying(256),
    search_id integer,
    status character varying(256),
    task_code character varying(256)
);


ALTER TABLE public.work_hour OWNER TO postgres;

--
-- Name: work_hour_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE work_hour_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.work_hour_id_seq OWNER TO postgres;

--
-- Name: work_hour_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE work_hour_id_seq OWNED BY work_hour.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE work_hour ALTER COLUMN id SET DEFAULT nextval('work_hour_id_seq'::regclass);


--
-- Name: work_hour_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY work_hour
    ADD CONSTRAINT work_hour_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: pga_layout; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_layout FROM PUBLIC;
REVOKE ALL ON TABLE pga_layout FROM postgres;
GRANT ALL ON TABLE pga_layout TO postgres;
GRANT ALL ON TABLE pga_layout TO PUBLIC;


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
-- PostgreSQL database dump complete
--

