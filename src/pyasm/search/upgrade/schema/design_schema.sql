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
-- Name: design; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE design (
    id serial NOT NULL,
    product_code character varying(30),
    code character varying(30) NOT NULL,
    description text,
    files text,
    "login" character varying(50),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    retire_status character varying(30),
    status text,
    snapshot text
);


ALTER TABLE public.design OWNER TO postgres;

--
-- Name: design_review; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE design_review (
    id serial NOT NULL,
    review_time timestamp without time zone,
    designs text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    retire_status character varying(30),
    description text
);


ALTER TABLE public.design_review OWNER TO postgres;

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
-- Name: product; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE product (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100),
    description text,
    "type" character varying(30),
    images text,
    "login" character varying(50),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    retire_status character varying(30)
);


ALTER TABLE public.product OWNER TO postgres;

--
-- Name: product_document; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE product_document (
    id serial NOT NULL,
    product_code character varying(30),
    description text,
    files text,
    "login" character varying(50),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    retire_status character varying(30),
    category character varying(100)
);


ALTER TABLE public.product_document OWNER TO postgres;

--
-- Name: product_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE product_type (
    code character varying(30) NOT NULL,
    description character varying(100)
);


ALTER TABLE public.product_type OWNER TO postgres;

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




CREATE TABLE naming (
    id serial NOT NULL,
    search_type character varying(100),
    dir_naming text,
    file_naming text
);


ALTER TABLE public.session_contents OWNER TO postgres;

--
-- Name: design_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY design
    ADD CONSTRAINT design_pkey PRIMARY KEY (code);


--
-- Name: design_review_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY design_review
    ADD CONSTRAINT design_review_pkey PRIMARY KEY (id);


--
-- Name: product_document_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY product_document
    ADD CONSTRAINT product_document_pkey PRIMARY KEY (id);


--
-- Name: product_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_pkey PRIMARY KEY (code);


--
-- Name: product_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY product_type
    ADD CONSTRAINT product_type_pkey PRIMARY KEY (code);


--
-- Name: session_contents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY session_contents
    ADD CONSTRAINT session_contents_pkey PRIMARY KEY (id);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY product
    ADD CONSTRAINT "$1" FOREIGN KEY ("type") REFERENCES product_type(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


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

