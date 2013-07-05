
-- DEPRECATED

--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- Name: pref_list_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pref_list_id_seq', 10, true);


--
-- Data for Name: pref_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (1, 'skin', 'These skins determine the look and feel of  TACTIC.', 'classic|dark|light|lightdark', 'sequence', 'general', '2007-06-07 16:01:32.593', 'Tactic Skins');
INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (2, 'language', 'The various language localizations', 'en_US|ja|nl', 'sequence', 'general', '2007-06-10 13:15:33.484', 'Language');
INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (3, 'thumb_multiplier', 'Determines the size multiplier of all thumbnail images', '1|2|0.5', 'sequence', 'general', '2007-06-11 10:10:06.203', 'Thumb Size');
INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (4, 'debug', 'Determines whether to show debug information', 'false|true', 'sequence', 'general', '2007-08-21 11:18:26.894318', 'Debug');
INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (5, 'select_filter', 'Determines whether to show some filters as multi-select', 'single|multi', 'sequence', 'general', '2008-03-01 11:18:26.894318', 'Select Filter');
INSERT INTO pref_list (id, "key", description, options, "type", category, "timestamp", title) VALUES (6, 'use_java_maya', 'Determines whether to use the java applet Maya connector', 'false|true', 'sequence', 'general', '2008-03-01 11:18:26.894318', 'Java Maya Connector');


--
-- PostgreSQL database dump complete
--

