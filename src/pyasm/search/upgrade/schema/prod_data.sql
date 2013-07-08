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
-- Name: asset_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('asset_type_id_seq', 5, true);


--
-- Data for Name: asset_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO asset_type (id, code, description) VALUES (1, 'asset', 'Asset');
INSERT INTO asset_type (id, code, description) VALUES (2, 'section', 'Section');
INSERT INTO asset_type (id, code, description) VALUES (3, 'set', 'Set');
INSERT INTO asset_type (id, code, description) VALUES (4, 'camera', 'Camera');
INSERT INTO asset_type (id, code, description) VALUES (5, 'set_item', 'Set Item');


--
-- PostgreSQL database dump complete
--

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
-- Name: prod_setting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('prod_setting_id_seq', 38, true);


--
-- Data for Name: prod_setting; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (1, 'task_2d_options', 'Plate Enhance|MatchMove / Track|Plate Stabalize|Rig Removal|2D Effects|Roto Masking|Paint Touch Up|Color and Light|Green Screen|Matte Painting|Bioluminescence', NULL, NULL, NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (2, 'task_3d_options', 'FX Animation|Environmental Effects|Volumetrics|Debris|3D MatchMove|Modeling|Texture Paint|Shadow Develop|Color Lighting', NULL, NULL, NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (3, 'task_anim_options', 'Facial Animation|Blocking|Primary Animation|Facial Animation|Secondary Animation|Secondary Facial', NULL, NULL, NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (4, 'sub_context', 'previs|anim|render|jojo', 'Checkin contexts options for assets', 'sequence', 'prod/asset', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (5, 'notes_director_context', '2D|FX|Anim|Misc', 'Different contexts for director''s notes', 'sequence', 'prod/note', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (6, 'texture_category', 'concept|texture|mattepainting|misc', 'The different categories for 2D assets', 'sequence', 'prod/texture', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (7, 'notes_preprod_context', 'Client Kick Off|Internal Kick Off', 'Preproduction notes categories', 'sequence', 'prod/note', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (8, 'bin_type', 'dailies|client', 'The different type of bins', 'sequence', 'prod/bin', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (9, 'texture/category', 'texture|mattepainting|concept', 'Various Types of 2D Assets', 'sequence', 'prod/texture', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (10, 'prod_notes', 'Client', 'Production notes categories', 'sequence', 'prod/shot', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (11, 'notes_prod_context', 'client|internal', 'Types of production contexts for notes', 'sequence', 'prod/asset', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (12, 'note_status', 'new:N|read:R|old:O|:-', 'Note Statuses', 'map', 'sthpw/note', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (13, 'bin_label', 'anim|tech|review|final', 'Bin Labels', 'sequence', 'prod/bin', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (14, 'art_reference_category', 'Concept|Reference|Inspiration', 'Categories for reference material', 'sequence', 'prod/art_reference', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (15, 'notes_client_context', 'client|client edited', 'Notes context for clients', 'sequence', 'sthpw/note', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (16, 'timecard_item', 'lunch|dinner|workout|coffee|meeting', 'Timecard Items', 'sequence', 'sthpw/timecard', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (17, 'show_instances_in_shot_tab', 'true', 'Show instances in shot tab', NULL, NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (18, 'client_note_status', '|Sent to Client|Feedback Received', 'Client Note Status', 'sequence', 'prod/submission', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (19, 'skin', 'lightdark', 'Tactic skin', 'string', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (20, 'notes_shot_context', 'setup|animation|lighting|compsiting', 'Notes options for the various processes', 'sequence', 'prod/bin', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (21, 'skin_options', 'classic|light|dark|lightdark', 'Skin Options', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (22, 'invisible_tabs/main_tab', NULL, 'invisible tabs for main_tab', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (23, 'invisible_tabs/asset_pipeline_tab', NULL, 'invisible tabs for asset_pipeline_tab', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (24, 'project_docs_url', 'http://yahoo.com', 'Project specific docs - Documentation written for this specific production', 'string', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (25, 'script_stage', 'Final Record Draft|Final Draft|Second Draft|First Draft|Outline|Pitch', 'Script stages', 'sequence', 'bell/human_resources/people', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (26, 'invisible_tabs/maya_tab', 'Layer Loader|Layer Checkin', 'invisible tabs for maya_tab', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (27, 'dailies_note_status', 'Waiting|Waiting Feedback|Comment Made', 'Dailies Notes Status', 'sequence', 'prod/submission', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (29, 'shot_scan_status', 'Turned Over|Scan Received|Scan Processed', 'Shot scan status', 'sequence', 'prod/shot', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (30, 'shot_type', '2D|Full CG|2D and 3D', 'Shot Types', 'sequence', 'prod/shot', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (31, 'invisible_elements', 'complexity|sort_order|custom', 'Invisible Elements for shots', 'sequence', 'prod/shot', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (32, 'invisible_elements', 'placeholder', 'Invisible Elements for assets', 'sequence', 'prod/asset', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (33, 'invisible_elements', 'milestone_code|priority', 'Invisible Elements for tasks', 'sequence', 'sthpw/task', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (28, 'shot_status', 'New|Omit|Hold|WIP|Pending Client|Pending Final|FINAL', 'Statuses of a shot', 'sequence', 'prod/shot', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (34, 'invisible_tabs', 'Sets', 'invisible tabs for true', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (35, 'reg_hours', '10', 'regular work hours', 'sequence', 'sthpw/project', 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (36, 'use_name_as_asset_code', 'false', 'Use name as the asset code', 'sequence', NULL, 'General');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (37, 'use_name_as_asset_code', 'false', 'Use name as the asset code', 'sequence', NULL, 'Naming');
INSERT INTO prod_setting (id, "key", value, description, "type", search_type, category) VALUES (38, 'handle_texture_dependency', 'true', 'handle texture dependency', 'sequence', NULL, NULL);


--
-- PostgreSQL database dump complete
--

