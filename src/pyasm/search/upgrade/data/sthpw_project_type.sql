

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
-- Name: project_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('project_type_id_seq', 12, true);


--
-- Data for Name: project_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO project_type (id, code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls, s_status, "type", repo_handler_cls) VALUES (12, 'simple', NULL, NULL, NULL, NULL, NULL, NULL, 'simple', NULL);
INSERT INTO project_type (id, code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls, s_status, "type", repo_handler_cls) VALUES (7, 'game', 'pyasm.prod.biz.ProdDirNaming', 'pyasm.prod.biz.ProdFileNaming', NULL, NULL, '	pyasm.game.biz.GameMapping', NULL, 'game', NULL);
INSERT INTO project_type (id, code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls, s_status, "type", repo_handler_cls) VALUES (1, 'prod', 'pyasm.prod.biz.ProdDirNaming', 'pyasm.prod.biz.ProdFileNaming', '', '', '', NULL, 'prod', NULL);
INSERT INTO project_type (id, code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls, s_status, "type", repo_handler_cls) VALUES (11, 'unittest', NULL, NULL, NULL, NULL, NULL, NULL, 'unittest', NULL);


--
-- PostgreSQL database dump complete
--

