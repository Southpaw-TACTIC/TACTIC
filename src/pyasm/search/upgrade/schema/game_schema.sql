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


--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: 
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- Name: gtsvector_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_in(cstring) RETURNS gtsvector
    AS '$libdir/tsearch2', 'gtsvector_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.gtsvector_in(cstring) OWNER TO postgres;

--
-- Name: gtsvector_out(gtsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_out(gtsvector) RETURNS cstring
    AS '$libdir/tsearch2', 'gtsvector_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.gtsvector_out(gtsvector) OWNER TO postgres;

--
-- Name: gtsvector; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE gtsvector (
    INTERNALLENGTH = variable,
    INPUT = gtsvector_in,
    OUTPUT = gtsvector_out,
    ALIGNMENT = int4,
    STORAGE = plain
);


ALTER TYPE public.gtsvector OWNER TO postgres;

--
-- Name: tsquery_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsquery_in(cstring) RETURNS tsquery
    AS '$libdir/tsearch2', 'tsquery_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.tsquery_in(cstring) OWNER TO postgres;

--
-- Name: tsquery_out(tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsquery_out(tsquery) RETURNS cstring
    AS '$libdir/tsearch2', 'tsquery_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.tsquery_out(tsquery) OWNER TO postgres;

--
-- Name: tsquery; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE tsquery (
    INTERNALLENGTH = variable,
    INPUT = tsquery_in,
    OUTPUT = tsquery_out,
    ALIGNMENT = int4,
    STORAGE = plain
);


ALTER TYPE public.tsquery OWNER TO postgres;

--
-- Name: tsvector_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_in(cstring) RETURNS tsvector
    AS '$libdir/tsearch2', 'tsvector_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.tsvector_in(cstring) OWNER TO postgres;

--
-- Name: tsvector_out(tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_out(tsvector) RETURNS cstring
    AS '$libdir/tsearch2', 'tsvector_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.tsvector_out(tsvector) OWNER TO postgres;

--
-- Name: tsvector; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE tsvector (
    INTERNALLENGTH = variable,
    INPUT = tsvector_in,
    OUTPUT = tsvector_out,
    ALIGNMENT = int4,
    STORAGE = extended
);


ALTER TYPE public.tsvector OWNER TO postgres;

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
-- Name: tsdebug; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE tsdebug AS (
	ts_name text,
	tok_type text,
	description text,
	token text,
	dict_name text[],
	tsvector tsvector
);


ALTER TYPE public.tsdebug OWNER TO postgres;

--
-- Name: _get_parser_from_curcfg(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _get_parser_from_curcfg() RETURNS text
    AS $$ select prs_name from pg_ts_cfg where oid = show_curcfg() $$
    LANGUAGE sql IMMUTABLE STRICT;


ALTER FUNCTION public._get_parser_from_curcfg() OWNER TO postgres;

--
-- Name: concat(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION concat(tsvector, tsvector) RETURNS tsvector
    AS '$libdir/tsearch2', 'concat'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.concat(tsvector, tsvector) OWNER TO postgres;

--
-- Name: dex_init(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION dex_init(internal) RETURNS internal
    AS '$libdir/tsearch2', 'dex_init'
    LANGUAGE c;


ALTER FUNCTION public.dex_init(internal) OWNER TO postgres;

--
-- Name: dex_lexize(internal, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION dex_lexize(internal, internal, integer) RETURNS internal
    AS '$libdir/tsearch2', 'dex_lexize'
    LANGUAGE c STRICT;


ALTER FUNCTION public.dex_lexize(internal, internal, integer) OWNER TO postgres;

--
-- Name: exectsq(tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION exectsq(tsvector, tsquery) RETURNS boolean
    AS '$libdir/tsearch2', 'exectsq'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.exectsq(tsvector, tsquery) OWNER TO postgres;

--
-- Name: FUNCTION exectsq(tsvector, tsquery); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION exectsq(tsvector, tsquery) IS 'boolean operation with text index';


--
-- Name: get_covers(tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION get_covers(tsvector, tsquery) RETURNS text
    AS '$libdir/tsearch2', 'get_covers'
    LANGUAGE c STRICT;


ALTER FUNCTION public.get_covers(tsvector, tsquery) OWNER TO postgres;

--
-- Name: gtsvector_compress(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_compress(internal) RETURNS internal
    AS '$libdir/tsearch2', 'gtsvector_compress'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_compress(internal) OWNER TO postgres;

--
-- Name: gtsvector_consistent(gtsvector, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_consistent(gtsvector, internal, integer) RETURNS boolean
    AS '$libdir/tsearch2', 'gtsvector_consistent'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_consistent(gtsvector, internal, integer) OWNER TO postgres;

--
-- Name: gtsvector_decompress(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_decompress(internal) RETURNS internal
    AS '$libdir/tsearch2', 'gtsvector_decompress'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_decompress(internal) OWNER TO postgres;

--
-- Name: gtsvector_penalty(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_penalty(internal, internal, internal) RETURNS internal
    AS '$libdir/tsearch2', 'gtsvector_penalty'
    LANGUAGE c STRICT;


ALTER FUNCTION public.gtsvector_penalty(internal, internal, internal) OWNER TO postgres;

--
-- Name: gtsvector_picksplit(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_picksplit(internal, internal) RETURNS internal
    AS '$libdir/tsearch2', 'gtsvector_picksplit'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_picksplit(internal, internal) OWNER TO postgres;

--
-- Name: gtsvector_same(gtsvector, gtsvector, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_same(gtsvector, gtsvector, internal) RETURNS internal
    AS '$libdir/tsearch2', 'gtsvector_same'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_same(gtsvector, gtsvector, internal) OWNER TO postgres;

--
-- Name: gtsvector_union(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION gtsvector_union(internal, internal) RETURNS integer[]
    AS '$libdir/tsearch2', 'gtsvector_union'
    LANGUAGE c;


ALTER FUNCTION public.gtsvector_union(internal, internal) OWNER TO postgres;

--
-- Name: headline(oid, text, tsquery, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(oid, text, tsquery, text) RETURNS text
    AS '$libdir/tsearch2', 'headline'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(oid, text, tsquery, text) OWNER TO postgres;

--
-- Name: headline(oid, text, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(oid, text, tsquery) RETURNS text
    AS '$libdir/tsearch2', 'headline'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(oid, text, tsquery) OWNER TO postgres;

--
-- Name: headline(text, text, tsquery, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(text, text, tsquery, text) RETURNS text
    AS '$libdir/tsearch2', 'headline_byname'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(text, text, tsquery, text) OWNER TO postgres;

--
-- Name: headline(text, text, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(text, text, tsquery) RETURNS text
    AS '$libdir/tsearch2', 'headline_byname'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(text, text, tsquery) OWNER TO postgres;

--
-- Name: headline(text, tsquery, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(text, tsquery, text) RETURNS text
    AS '$libdir/tsearch2', 'headline_current'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(text, tsquery, text) OWNER TO postgres;

--
-- Name: headline(text, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION headline(text, tsquery) RETURNS text
    AS '$libdir/tsearch2', 'headline_current'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.headline(text, tsquery) OWNER TO postgres;

--
-- Name: length(tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION length(tsvector) RETURNS integer
    AS '$libdir/tsearch2', 'tsvector_length'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.length(tsvector) OWNER TO postgres;

--
-- Name: lexize(oid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lexize(oid, text) RETURNS text[]
    AS '$libdir/tsearch2', 'lexize'
    LANGUAGE c STRICT;


ALTER FUNCTION public.lexize(oid, text) OWNER TO postgres;

--
-- Name: lexize(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lexize(text, text) RETURNS text[]
    AS '$libdir/tsearch2', 'lexize_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.lexize(text, text) OWNER TO postgres;

--
-- Name: lexize(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lexize(text) RETURNS text[]
    AS '$libdir/tsearch2', 'lexize_bycurrent'
    LANGUAGE c STRICT;


ALTER FUNCTION public.lexize(text) OWNER TO postgres;

--
-- Name: parse(oid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION parse(oid, text) RETURNS SETOF tokenout
    AS '$libdir/tsearch2', 'parse'
    LANGUAGE c STRICT;


ALTER FUNCTION public.parse(oid, text) OWNER TO postgres;

--
-- Name: parse(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION parse(text, text) RETURNS SETOF tokenout
    AS '$libdir/tsearch2', 'parse_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.parse(text, text) OWNER TO postgres;

--
-- Name: parse(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION parse(text) RETURNS SETOF tokenout
    AS '$libdir/tsearch2', 'parse_current'
    LANGUAGE c STRICT;


ALTER FUNCTION public.parse(text) OWNER TO postgres;

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

--
-- Name: prsd_end(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION prsd_end(internal) RETURNS void
    AS '$libdir/tsearch2', 'prsd_end'
    LANGUAGE c;


ALTER FUNCTION public.prsd_end(internal) OWNER TO postgres;

--
-- Name: prsd_getlexeme(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION prsd_getlexeme(internal, internal, internal) RETURNS integer
    AS '$libdir/tsearch2', 'prsd_getlexeme'
    LANGUAGE c;


ALTER FUNCTION public.prsd_getlexeme(internal, internal, internal) OWNER TO postgres;

--
-- Name: prsd_headline(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION prsd_headline(internal, internal, internal) RETURNS internal
    AS '$libdir/tsearch2', 'prsd_headline'
    LANGUAGE c;


ALTER FUNCTION public.prsd_headline(internal, internal, internal) OWNER TO postgres;

--
-- Name: prsd_lextype(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION prsd_lextype(internal) RETURNS internal
    AS '$libdir/tsearch2', 'prsd_lextype'
    LANGUAGE c;


ALTER FUNCTION public.prsd_lextype(internal) OWNER TO postgres;

--
-- Name: prsd_start(internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION prsd_start(internal, integer) RETURNS internal
    AS '$libdir/tsearch2', 'prsd_start'
    LANGUAGE c;


ALTER FUNCTION public.prsd_start(internal, integer) OWNER TO postgres;

--
-- Name: querytree(tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION querytree(tsquery) RETURNS text
    AS '$libdir/tsearch2', 'tsquerytree'
    LANGUAGE c STRICT;


ALTER FUNCTION public.querytree(tsquery) OWNER TO postgres;

--
-- Name: rank(real[], tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank(real[], tsvector, tsquery) RETURNS real
    AS '$libdir/tsearch2', 'rank'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank(real[], tsvector, tsquery) OWNER TO postgres;

--
-- Name: rank(real[], tsvector, tsquery, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank(real[], tsvector, tsquery, integer) RETURNS real
    AS '$libdir/tsearch2', 'rank'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank(real[], tsvector, tsquery, integer) OWNER TO postgres;

--
-- Name: rank(tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank(tsvector, tsquery) RETURNS real
    AS '$libdir/tsearch2', 'rank_def'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank(tsvector, tsquery) OWNER TO postgres;

--
-- Name: rank(tsvector, tsquery, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank(tsvector, tsquery, integer) RETURNS real
    AS '$libdir/tsearch2', 'rank_def'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank(tsvector, tsquery, integer) OWNER TO postgres;

--
-- Name: rank_cd(integer, tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank_cd(integer, tsvector, tsquery) RETURNS real
    AS '$libdir/tsearch2', 'rank_cd'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank_cd(integer, tsvector, tsquery) OWNER TO postgres;

--
-- Name: rank_cd(integer, tsvector, tsquery, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank_cd(integer, tsvector, tsquery, integer) RETURNS real
    AS '$libdir/tsearch2', 'rank_cd'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank_cd(integer, tsvector, tsquery, integer) OWNER TO postgres;

--
-- Name: rank_cd(tsvector, tsquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank_cd(tsvector, tsquery) RETURNS real
    AS '$libdir/tsearch2', 'rank_cd_def'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank_cd(tsvector, tsquery) OWNER TO postgres;

--
-- Name: rank_cd(tsvector, tsquery, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rank_cd(tsvector, tsquery, integer) RETURNS real
    AS '$libdir/tsearch2', 'rank_cd_def'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rank_cd(tsvector, tsquery, integer) OWNER TO postgres;

--
-- Name: reset_tsearch(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION reset_tsearch() RETURNS void
    AS '$libdir/tsearch2', 'reset_tsearch'
    LANGUAGE c STRICT;


ALTER FUNCTION public.reset_tsearch() OWNER TO postgres;

--
-- Name: rexectsq(tsquery, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rexectsq(tsquery, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'rexectsq'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rexectsq(tsquery, tsvector) OWNER TO postgres;

--
-- Name: FUNCTION rexectsq(tsquery, tsvector); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION rexectsq(tsquery, tsvector) IS 'boolean operation with text index';


--
-- Name: set_curcfg(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curcfg(integer) RETURNS void
    AS '$libdir/tsearch2', 'set_curcfg'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curcfg(integer) OWNER TO postgres;

--
-- Name: set_curcfg(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curcfg(text) RETURNS void
    AS '$libdir/tsearch2', 'set_curcfg_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curcfg(text) OWNER TO postgres;

--
-- Name: set_curdict(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curdict(integer) RETURNS void
    AS '$libdir/tsearch2', 'set_curdict'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curdict(integer) OWNER TO postgres;

--
-- Name: set_curdict(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curdict(text) RETURNS void
    AS '$libdir/tsearch2', 'set_curdict_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curdict(text) OWNER TO postgres;

--
-- Name: set_curprs(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curprs(integer) RETURNS void
    AS '$libdir/tsearch2', 'set_curprs'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curprs(integer) OWNER TO postgres;

--
-- Name: set_curprs(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_curprs(text) RETURNS void
    AS '$libdir/tsearch2', 'set_curprs_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.set_curprs(text) OWNER TO postgres;

--
-- Name: setweight(tsvector, "char"); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION setweight(tsvector, "char") RETURNS tsvector
    AS '$libdir/tsearch2', 'setweight'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.setweight(tsvector, "char") OWNER TO postgres;

--
-- Name: show_curcfg(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION show_curcfg() RETURNS oid
    AS '$libdir/tsearch2', 'show_curcfg'
    LANGUAGE c STRICT;


ALTER FUNCTION public.show_curcfg() OWNER TO postgres;

--
-- Name: snb_en_init(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION snb_en_init(internal) RETURNS internal
    AS '$libdir/tsearch2', 'snb_en_init'
    LANGUAGE c;


ALTER FUNCTION public.snb_en_init(internal) OWNER TO postgres;

--
-- Name: snb_lexize(internal, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION snb_lexize(internal, internal, integer) RETURNS internal
    AS '$libdir/tsearch2', 'snb_lexize'
    LANGUAGE c STRICT;


ALTER FUNCTION public.snb_lexize(internal, internal, integer) OWNER TO postgres;

--
-- Name: snb_ru_init(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION snb_ru_init(internal) RETURNS internal
    AS '$libdir/tsearch2', 'snb_ru_init'
    LANGUAGE c;


ALTER FUNCTION public.snb_ru_init(internal) OWNER TO postgres;

--
-- Name: spell_init(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION spell_init(internal) RETURNS internal
    AS '$libdir/tsearch2', 'spell_init'
    LANGUAGE c;


ALTER FUNCTION public.spell_init(internal) OWNER TO postgres;

--
-- Name: spell_lexize(internal, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION spell_lexize(internal, internal, integer) RETURNS internal
    AS '$libdir/tsearch2', 'spell_lexize'
    LANGUAGE c STRICT;


ALTER FUNCTION public.spell_lexize(internal, internal, integer) OWNER TO postgres;

--
-- Name: stat(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION stat(text) RETURNS SETOF statinfo
    AS '$libdir/tsearch2', 'ts_stat'
    LANGUAGE c STRICT;


ALTER FUNCTION public.stat(text) OWNER TO postgres;

--
-- Name: stat(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION stat(text, text) RETURNS SETOF statinfo
    AS '$libdir/tsearch2', 'ts_stat'
    LANGUAGE c STRICT;


ALTER FUNCTION public.stat(text, text) OWNER TO postgres;

--
-- Name: strip(tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION strip(tsvector) RETURNS tsvector
    AS '$libdir/tsearch2', 'strip'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.strip(tsvector) OWNER TO postgres;

--
-- Name: syn_init(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION syn_init(internal) RETURNS internal
    AS '$libdir/tsearch2', 'syn_init'
    LANGUAGE c;


ALTER FUNCTION public.syn_init(internal) OWNER TO postgres;

--
-- Name: syn_lexize(internal, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION syn_lexize(internal, internal, integer) RETURNS internal
    AS '$libdir/tsearch2', 'syn_lexize'
    LANGUAGE c STRICT;


ALTER FUNCTION public.syn_lexize(internal, internal, integer) OWNER TO postgres;

--
-- Name: to_tsquery(oid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsquery(oid, text) RETURNS tsquery
    AS '$libdir/tsearch2', 'to_tsquery'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsquery(oid, text) OWNER TO postgres;

--
-- Name: to_tsquery(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsquery(text, text) RETURNS tsquery
    AS '$libdir/tsearch2', 'to_tsquery_name'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsquery(text, text) OWNER TO postgres;

--
-- Name: to_tsquery(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsquery(text) RETURNS tsquery
    AS '$libdir/tsearch2', 'to_tsquery_current'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsquery(text) OWNER TO postgres;

--
-- Name: to_tsvector(oid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsvector(oid, text) RETURNS tsvector
    AS '$libdir/tsearch2', 'to_tsvector'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsvector(oid, text) OWNER TO postgres;

--
-- Name: to_tsvector(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsvector(text, text) RETURNS tsvector
    AS '$libdir/tsearch2', 'to_tsvector_name'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsvector(text, text) OWNER TO postgres;

--
-- Name: to_tsvector(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION to_tsvector(text) RETURNS tsvector
    AS '$libdir/tsearch2', 'to_tsvector_current'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.to_tsvector(text) OWNER TO postgres;

--
-- Name: token_type(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION token_type(integer) RETURNS SETOF tokentype
    AS '$libdir/tsearch2', 'token_type'
    LANGUAGE c STRICT;


ALTER FUNCTION public.token_type(integer) OWNER TO postgres;

--
-- Name: token_type(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION token_type(text) RETURNS SETOF tokentype
    AS '$libdir/tsearch2', 'token_type_byname'
    LANGUAGE c STRICT;


ALTER FUNCTION public.token_type(text) OWNER TO postgres;

--
-- Name: token_type(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION token_type() RETURNS SETOF tokentype
    AS '$libdir/tsearch2', 'token_type_current'
    LANGUAGE c STRICT;


ALTER FUNCTION public.token_type() OWNER TO postgres;

--
-- Name: ts_debug(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ts_debug(text) RETURNS SETOF tsdebug
    AS $_$
select 
        m.ts_name,
        t.alias as tok_type,
        t.descr as description,
        p.token,
        m.dict_name,
        strip(to_tsvector(p.token)) as tsvector
from
        parse( _get_parser_from_curcfg(), $1 ) as p,
        token_type() as t,
        pg_ts_cfgmap as m,
        pg_ts_cfg as c
where
        t.tokid=p.tokid and
        t.alias = m.tok_alias and 
        m.ts_name=c.ts_name and 
        c.oid=show_curcfg() 
$_$
    LANGUAGE sql STRICT;


ALTER FUNCTION public.ts_debug(text) OWNER TO postgres;

--
-- Name: tsearch2(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsearch2() RETURNS "trigger"
    AS '$libdir/tsearch2', 'tsearch2'
    LANGUAGE c;


ALTER FUNCTION public.tsearch2() OWNER TO postgres;

--
-- Name: tsvector_cmp(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_cmp(tsvector, tsvector) RETURNS integer
    AS '$libdir/tsearch2', 'tsvector_cmp'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_cmp(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_eq(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_eq(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_eq'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_eq(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_ge(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_ge(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_ge'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_ge(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_gt(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_gt(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_gt'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_gt(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_le(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_le(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_le'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_le(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_lt(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_lt(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_lt'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_lt(tsvector, tsvector) OWNER TO postgres;

--
-- Name: tsvector_ne(tsvector, tsvector); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tsvector_ne(tsvector, tsvector) RETURNS boolean
    AS '$libdir/tsearch2', 'tsvector_ne'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.tsvector_ne(tsvector, tsvector) OWNER TO postgres;

--
-- Name: <; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR < (
    PROCEDURE = tsvector_lt,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = >,
    NEGATOR = >=,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.< (tsvector, tsvector) OWNER TO postgres;

--
-- Name: <=; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <= (
    PROCEDURE = tsvector_le,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = >=,
    NEGATOR = >,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<= (tsvector, tsvector) OWNER TO postgres;

--
-- Name: <>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <> (
    PROCEDURE = tsvector_ne,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = <>,
    NEGATOR = =,
    RESTRICT = neqsel,
    JOIN = neqjoinsel
);


ALTER OPERATOR public.<> (tsvector, tsvector) OWNER TO postgres;

--
-- Name: =; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR = (
    PROCEDURE = tsvector_eq,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = =,
    NEGATOR = <>,
    RESTRICT = eqsel,
    JOIN = eqjoinsel,
    SORT1 = <,
    SORT2 = <,
    LTCMP = <,
    GTCMP = >
);


ALTER OPERATOR public.= (tsvector, tsvector) OWNER TO postgres;

--
-- Name: >; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR > (
    PROCEDURE = tsvector_gt,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = <,
    NEGATOR = <=,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.> (tsvector, tsvector) OWNER TO postgres;

--
-- Name: >=; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR >= (
    PROCEDURE = tsvector_ge,
    LEFTARG = tsvector,
    RIGHTARG = tsvector,
    COMMUTATOR = <=,
    NEGATOR = <,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.>= (tsvector, tsvector) OWNER TO postgres;

--
-- Name: @@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @@ (
    PROCEDURE = exectsq,
    LEFTARG = tsvector,
    RIGHTARG = tsquery,
    COMMUTATOR = @@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@@ (tsvector, tsquery) OWNER TO postgres;

--
-- Name: @@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @@ (
    PROCEDURE = rexectsq,
    LEFTARG = tsquery,
    RIGHTARG = tsvector,
    COMMUTATOR = @@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@@ (tsquery, tsvector) OWNER TO postgres;

--
-- Name: ||; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR || (
    PROCEDURE = concat,
    LEFTARG = tsvector,
    RIGHTARG = tsvector
);


ALTER OPERATOR public.|| (tsvector, tsvector) OWNER TO postgres;

--
-- Name: gist_tsvector_ops; Type: OPERATOR CLASS; Schema: public; Owner: postgres
--

CREATE OPERATOR CLASS gist_tsvector_ops
    DEFAULT FOR TYPE tsvector USING gist AS
    STORAGE gtsvector ,
    OPERATOR 1 @@(tsvector,tsquery) RECHECK ,
    FUNCTION 1 gtsvector_consistent(gtsvector,internal,integer) ,
    FUNCTION 2 gtsvector_union(internal,internal) ,
    FUNCTION 3 gtsvector_compress(internal) ,
    FUNCTION 4 gtsvector_decompress(internal) ,
    FUNCTION 5 gtsvector_penalty(internal,internal,internal) ,
    FUNCTION 6 gtsvector_picksplit(internal,internal) ,
    FUNCTION 7 gtsvector_same(gtsvector,gtsvector,internal);


ALTER OPERATOR CLASS public.gist_tsvector_ops USING gist OWNER TO postgres;

--
-- Name: tsvector_ops; Type: OPERATOR CLASS; Schema: public; Owner: postgres
--

CREATE OPERATOR CLASS tsvector_ops
    DEFAULT FOR TYPE tsvector USING btree AS
    OPERATOR 1 <(tsvector,tsvector) ,
    OPERATOR 2 <=(tsvector,tsvector) ,
    OPERATOR 3 =(tsvector,tsvector) ,
    OPERATOR 4 >=(tsvector,tsvector) ,
    OPERATOR 5 >(tsvector,tsvector) ,
    FUNCTION 1 tsvector_cmp(tsvector,tsvector);


ALTER OPERATOR CLASS public.tsvector_ops USING btree OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: art_reference; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE art_reference (
    id serial NOT NULL,
    code character varying(256),
    name character varying(200),
    description text,
    snapshot text,
    category character varying(100)
);


ALTER TABLE public.art_reference OWNER TO postgres;

--
-- Name: asset; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    asset_type character varying(30),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    images text,
    status text,
    discussion text,
    snapshot text,
    retire_status character varying(30),
    asset_library character varying(100),
    pipeline_code character varying(256),
    s_status character varying(30),
    perforce_path character varying(200)
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
    pipeline text,
    s_status character varying(30),
    repo_path character varying(200)
);


ALTER TABLE public.asset_library OWNER TO postgres;

--
-- Name: asset_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE asset_type (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    title character varying(100),
    asset_type character varying(100),
    description text,
    padding smallint DEFAULT 3
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
-- Name: composite; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE composite (
    id serial NOT NULL,
    name character varying(100),
    description text,
    shot_code character varying(100),
    snapshot text,
    "timestamp" timestamp without time zone DEFAULT now(),
    llll character varying(256),
    coco text
);


ALTER TABLE public.composite OWNER TO postgres;


--
-- Name: custom_property; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 

CREATE TABLE custom_property (
    id serial NOT NULL,
    search_type varchar(256),
    name varchar(256),
    description text,
    login varchar(256),
    PRIMARY KEY (id)
);

--
-- Name: env_source_asset; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE env_source_asset (
    id serial NOT NULL,
    category character varying(200),
    name character varying(200),
    description text,
    keywords text,
    snapshot text,
    repo_path character varying(200)
);


ALTER TABLE public.env_source_asset OWNER TO postgres;

--
-- Name: instance; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE instance (
    id serial NOT NULL,
    level_code character varying(30) NOT NULL,
    asset_code character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    "type" character varying(30),
    pipeline_code varying(256)
);


ALTER TABLE public.instance OWNER TO postgres;

--
-- Name: layer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE layer (
    id serial NOT NULL,
    name character varying(100),
    description text,
    level_code character varying(100),
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
    layer_id character varying(100) NOT NULL,
    "type" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    name character varying(100)
);


ALTER TABLE public.layer_instance OWNER TO postgres;

--
-- Name: level; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "level" (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    status text,
    discussion text,
    images text,
    tc_frame_start smallint DEFAULT 1,
    tc_frame_end smallint DEFAULT 1,
    pipeline character varying(30),
    parent_code character varying(30),
    s_status character varying(30),
    sort_order smallint
);


ALTER TABLE public."level" OWNER TO postgres;

--
-- Name: node_data; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE node_data (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    data text
);


ALTER TABLE public.node_data OWNER TO postgres;

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

SET default_with_oids = false;

--
-- Name: pga_forms; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_forms (
    formname character varying(64),
    formsource text
);


ALTER TABLE public.pga_forms OWNER TO postgres;

SET default_with_oids = true;

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
-- Name: pga_scripts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_scripts (
    scriptname character varying(64),
    scriptsource text
);


ALTER TABLE public.pga_scripts OWNER TO postgres;

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
    snapshot_code character varying(30)
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
-- Name: sequence; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "sequence" (
    id serial NOT NULL,
    code character varying(30) NOT NULL,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    sort_order smallint
);


ALTER TABLE public."sequence" OWNER TO postgres;

--
-- Name: session_contents; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE session_contents (
    id serial NOT NULL,
    "login" character varying(100),
    pid integer,
    data text,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.session_contents OWNER TO postgres;

--
-- Name: source_asset; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE source_asset (
    id serial NOT NULL,
    category character varying(200),
    name character varying(200),
    description text,
    keywords text,
    snapshot text,
    repo_path character varying(200)
);


ALTER TABLE public.source_asset OWNER TO postgres;

--
-- Name: storyboard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE storyboard (
    id serial NOT NULL,
    files text,
    "timestamp" timestamp without time zone DEFAULT now(),
    code character varying(30),
    level_code character varying(30),
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
    artist character varying(30),
    "login" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30)
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
    pipeline character varying(30)
);


ALTER TABLE public.texture OWNER TO postgres;

--
-- Name: texture_source; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE texture_source (
    id serial NOT NULL,
    description text,
    asset_code character varying(30) NOT NULL,
    category character varying(200) NOT NULL,
    "timestamp" timestamp without time zone,
    s_status character varying(32),
    code character varying(100) NOT NULL
);


ALTER TABLE public.texture_source OWNER TO postgres;

--
-- Name: timecard; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE timecard (
    id serial NOT NULL,
    search_type character varying(100),
    search_id integer,
    week smallint,
    mon real,
    tue real,
    wed real,
    thu real,
    fri real,
    sat real,
    sun real
);


ALTER TABLE public.timecard OWNER TO postgres;



CREATE TABLE naming (
    id serial NOT NULL,
    search_type character varying(100),
    dir_naming text,
    file_naming text
);



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
-- Name: composite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY composite
    ADD CONSTRAINT composite_pkey PRIMARY KEY (id);


--
-- Name: env_source_asset_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY env_source_asset
    ADD CONSTRAINT env_source_asset_pkey PRIMARY KEY (id);


--
-- Name: instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT instance_pkey PRIMARY KEY (id);


--
-- Name: instance_shot_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT instance_shot_code_key UNIQUE (level_code, name);


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
-- Name: node_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY node_data
    ADD CONSTRAINT node_data_pkey PRIMARY KEY (id);


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
-- Name: shot_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "level"
    ADD CONSTRAINT shot_code_key UNIQUE (code);


--
-- Name: shot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "level"
    ADD CONSTRAINT shot_pkey PRIMARY KEY (code);


--
-- Name: source_asset_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY source_asset
    ADD CONSTRAINT source_asset_pkey PRIMARY KEY (id);


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
-- Name: art_reference_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX art_reference_idx ON art_reference USING btree (name);


--
-- Name: env_source_asset_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX env_source_asset_idx ON env_source_asset USING btree (keywords);


--
-- Name: session_contents_pid_index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX session_contents_pid_index ON session_contents USING btree (pid);


--
-- Name: source_asset_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX source_asset_idx ON source_asset USING btree (keywords);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT "$1" FOREIGN KEY (level_code) REFERENCES "level"(code);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer
    ADD CONSTRAINT "$1" FOREIGN KEY (level_code) REFERENCES "level"(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY composite
    ADD CONSTRAINT "$1" FOREIGN KEY (shot_code) REFERENCES "level"(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY texture
    ADD CONSTRAINT "$1" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer_instance
    ADD CONSTRAINT "$1" FOREIGN KEY (layer_id) REFERENCES layer(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY instance
    ADD CONSTRAINT "$2" FOREIGN KEY (asset_code) REFERENCES asset(code);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY layer_instance
    ADD CONSTRAINT "$2" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


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
-- Name: pga_scripts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_scripts FROM PUBLIC;
REVOKE ALL ON TABLE pga_scripts FROM postgres;
GRANT ALL ON TABLE pga_scripts TO postgres;
GRANT ALL ON TABLE pga_scripts TO PUBLIC;


--
-- PostgreSQL database dump complete
--

