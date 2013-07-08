--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET check_function_bodies = false;
SET client_min_messages = warning;

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
    id serial NOT NULL,
    description text,
    snapshot text,
    category character varying(256),
    s_status character varying(30),
    keywords text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.art_reference OWNER TO postgres;

--
-- Name: asset; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    asset_type character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    images text,
    status text,
    snapshot text,
    retire_status character varying(30),
    asset_library character varying(100),
    pipeline_code character varying(256),
    s_status character varying(30)
);


ALTER TABLE public.asset OWNER TO postgres;

--
-- Name: asset_library; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset_library (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    title character varying(100),
    description text,
    padding smallint,
    "type" character varying(30),
    s_status character varying(30)
);


ALTER TABLE public.asset_library OWNER TO postgres;

--
-- Name: asset_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset_type (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text
);


ALTER TABLE public.asset_type OWNER TO postgres;

--
-- Name: bin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE bin (
    id serial NOT NULL,
    code character varying(256),
    description text,
    "type" character varying(100),
    s_status character varying(30),
    label character varying(100)
);


ALTER TABLE public.bin OWNER TO postgres;

--
-- Name: camera; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE camera (
    id serial NOT NULL,
    shot_code character varying(30),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30)
);


ALTER TABLE public.camera OWNER TO postgres;

--
-- Name: composite; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE composite (
    id serial NOT NULL,
    name character varying(100),
    description text,
    shot_code character varying(100),
    snapshot text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.composite OWNER TO postgres;

--
-- Name: cut_sequence; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cut_sequence (
    id serial NOT NULL,
    shot_code character varying(30),
    "type" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    description text,
    sequence_code character varying(100)
);


ALTER TABLE public.cut_sequence OWNER TO postgres;

--
-- Name: geo_cache; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE geo_cache (
    id serial NOT NULL,
    shot_code character varying(256),
    instance character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30)
);


ALTER TABLE public.geo_cache OWNER TO postgres;

--
-- Name: instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE instance (
    id serial NOT NULL,
    shot_code character varying(30) NOT NULL,
    asset_code character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    "type" character varying(30)
);


ALTER TABLE public.instance OWNER TO postgres;

--
-- Name: layer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE layer (
    id serial NOT NULL,
    name character varying(100),
    description text,
    shot_code character varying(100),
    snapshot text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.layer OWNER TO postgres;

--
-- Name: layer_instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE layer_instance (
    id serial NOT NULL,
    asset_code character varying(100) NOT NULL,
    "type" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    name character varying(100),
    layer_id integer
);


ALTER TABLE public.layer_instance OWNER TO postgres;

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
    id serial NOT NULL,
    shot_code character varying(30),
    "type" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    description text
);


ALTER TABLE public.plate OWNER TO postgres;

--
-- Name: process; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE process (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.process OWNER TO postgres;

--
-- Name: prod_setting; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE prod_setting (
    id serial NOT NULL,
    "key" character varying(100),
    value text,
    description text,
    "type" character varying(30),
    search_type character varying(200)
);


ALTER TABLE public.prod_setting OWNER TO postgres;

--
-- Name: render; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE render (
    id serial NOT NULL,
    images text,
    "session" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    snapshot text,
    search_type character varying(100),
    search_id integer,
    snapshot_code character varying(30),
    version smallint,
    file_range character varying(200)
);


ALTER TABLE public.render OWNER TO postgres;

--
-- Name: render_stage; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE render_stage (
    id serial NOT NULL,
    search_type character varying(100),
    search_id integer,
    context character varying(30),
    snapshot text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.render_stage OWNER TO postgres;

--
-- Name: script; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE script (
    id serial NOT NULL,
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
-- Name: sequence; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "sequence" (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    sort_order smallint
);


ALTER TABLE public."sequence" OWNER TO postgres;

--
-- Name: session_contents; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE session_contents (
    id serial NOT NULL,
    "login" character varying(100) NOT NULL,
    pid integer NOT NULL,
    data text,
    "timestamp" timestamp without time zone DEFAULT now()
);


ALTER TABLE public.session_contents OWNER TO postgres;

--
-- Name: shot; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    images text,
    tc_frame_start smallint DEFAULT 1,
    tc_frame_end smallint DEFAULT 1,
    pipeline_code character varying(30),
    s_status character varying(30),
    parent_code character varying(30),
    sequence_code character varying(30),
    sort_order smallint,
    complexity smallint,
    frame_in smallint,
    frame_out smallint,
    frame_note text,
    scan_status character varying(256),
    "type" character varying(256)
);


ALTER TABLE public.shot OWNER TO postgres;

--
-- Name: shot_audio; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_audio (
    id serial NOT NULL,
    title character varying(30),
    shot_code character varying(100)
);


ALTER TABLE public.shot_audio OWNER TO postgres;

--
-- Name: shot_definition; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_definition (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    pipeline character varying(30) NOT NULL
);


ALTER TABLE public.shot_definition OWNER TO postgres;

--
-- Name: shot_texture; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE shot_texture (
    id serial NOT NULL,
    description text,
    shot_code character varying(50),
    category character varying(200),
    "timestamp" timestamp without time zone DEFAULT now(),
    snapshot text,
    s_status character varying(32),
    code character varying(50),
    pipeline_code character varying(256),
    asset_context character varying(30),
    search_type character varying(256),
    search_id integer
);


ALTER TABLE public.shot_texture OWNER TO postgres;

--
-- Name: storyboard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE storyboard (
    id serial NOT NULL,
    files text,
    "timestamp" timestamp without time zone DEFAULT now(),
    code character varying(30),
    shot_code character varying(30),
    description text
);


ALTER TABLE public.storyboard OWNER TO postgres;

--
-- Name: submission; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE submission (
    id serial NOT NULL,
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
-- Name: submission_in_bin; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE submission_in_bin (
    id serial NOT NULL,
    submission_id integer NOT NULL,
    bin_id integer NOT NULL
);


ALTER TABLE public.submission_in_bin OWNER TO postgres;

--
-- Name: texture; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE texture (
    id serial NOT NULL,
    description text,
    asset_code character varying(50),
    category character varying(200),
    "timestamp" timestamp without time zone DEFAULT now(),
    snapshot text,
    s_status character varying(32),
    code character varying(50),
    pipeline character varying(30),
    pipeline_code character varying(30),
    asset_context character varying(30)
);


ALTER TABLE public.texture OWNER TO postgres;

--
-- Name: texture_source; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE texture_source (
    id serial NOT NULL,
    description text,
    asset_code character varying(50),
    category character varying(200),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32),
    code character varying(100)
);


ALTER TABLE public.texture_source OWNER TO postgres;

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
-- Name: cut_sequence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY cut_sequence
    ADD CONSTRAINT cut_sequence_pkey PRIMARY KEY (id);


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
-- Name: prod_setting_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX prod_setting_name_idx ON prod_setting USING btree ("key");


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

ALTER TABLE ONLY instance
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

