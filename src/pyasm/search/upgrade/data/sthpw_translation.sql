
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
-- Name: translation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('translation_id_seq', 42, true);


--
-- Data for Name: translation; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (59, 'ja', 'sobject n/a for snapshot code[%s]', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetile_wdg.py:215', NULL, '2007-06-16 13:56:08.703');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (60, 'ja', 'This is a dynamic string ''%s''', 'cowcowcow "%s"', 'C:/Program Files/Southpaw/Tactic/src/pyasmwebapp_server.py:307', NULL, '2007-06-16 13:58:17.906');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (83, 'fr', 'Editorial', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteeditorial_tab_wdg.py:24', NULL, '2007-06-16 16:57:36.343');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (84, 'fr', 'Dailies', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteeditorial_tab_wdg.py:26', NULL, '2007-06-16 16:57:36.343');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (61, 'fr', 'Projects', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:40', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (62, 'fr', 'Project Types', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:41', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (63, 'fr', 'Users', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:42', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (64, 'fr', 'Pipelines', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:43', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (65, 'fr', 'Triggers', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:44', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (66, 'fr', 'Notifications', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:45', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (67, 'fr', 'Exception Log', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:48', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (68, 'fr', 'Remote Repo', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:49', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (69, 'fr', 'Translations', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:50', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (70, 'fr', 'Preferences', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:51', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (71, 'fr', 'Undo Browser', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:52', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (85, 'fr', 'Asset List', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:36', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (86, 'fr', 'Summary', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:37', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (87, 'fr', 'Tasks', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:38', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (88, 'fr', 'Artist (3D Assets)', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:39', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (89, 'fr', 'Supe (3D Assets)', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:40', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (90, 'fr', '2D Assets', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:41', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (91, 'fr', 'Render Log', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:42', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (92, 'fr', 'Asset Libraries', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:43', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (93, 'fr', 'History', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:44', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (94, 'fr', 'Notes', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:45', NULL, '2007-06-16 16:59:59.171');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (72, 'fr', 'My Tactic', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:46', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (73, 'fr', 'Preproduction', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:47', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (74, 'fr', 'Asset Pipeline', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:48', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (75, 'fr', 'Shot Pipeline', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:49', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (76, 'fr', 'Overview', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:51', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (77, 'fr', 'Client', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:52', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (78, 'fr', 'Undo', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1285', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (79, 'fr', 'Admin', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:54', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (82, 'fr', 'Refresh', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgeticon_wdg.py:235', NULL, '2007-06-16 16:05:33.14');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (80, 'fr', 'Redo', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1312', NULL, '2007-06-16 15:47:46.875');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (48, 'ja', 'Projects', '&#12503;&#12525;&#12472;&#12455;&#12463;&#12488;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:40', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (49, 'ja', 'Project Types', '&#12503;&#12525;&#12472;&#12455;&#12463;&#12488;&#12398;&#31278;&#39006;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:41', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (50, 'ja', 'Users', '&#12518;&#12540;&#12470;&#12540;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:42', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (51, 'ja', 'Pipelines', '&#12497;&#12452;&#12503;&#12521;&#12452;&#12531;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:43', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (52, 'ja', 'Triggers', '&#12488;&#12522;&#12460;&#12540;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:44', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (53, 'ja', 'Notifications', '&#35686;&#21578;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:39', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (56, 'ja', 'Translations', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:50', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (54, 'ja', 'Exception Log', '&#12456;&#12463;&#12475;&#12503;&#12471;&#12519;&#12531;&#12539;&#12525;&#12464;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:48', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (55, 'ja', 'Remote Repo', '&#12522;&#12514;&#12540;&#12488;&#12539;&#12524;&#12509;', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:49', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (57, 'ja', 'Preferences', '&#12503;&#12522;&#12501;&#12449;&#12524;&#12531;&#12473;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:42', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (58, 'ja', 'Undo Browser', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:52', NULL, '2007-06-16 12:29:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (105, 'ja', 'Language', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:74', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (112, 'ja', 'Show only untranslated', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:85', NULL, '2007-06-20 14:37:45.156');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (107, 'ja', '%s upload is required', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmcommandedit_wdg_action.py:352', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (95, 'ja', 'Asset List', '&#12450;&#12475;&#12483;&#12488;&#12539;&#12522;&#12473;&#12488;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:36', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (96, 'ja', 'Summary', '&#12469;&#12510;&#12522;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:37', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (97, 'ja', 'Tasks', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:38', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (98, 'ja', 'Artist (3D Assets)', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:39', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (99, 'ja', 'Supe (3D Assets)', '&#12473;&#12540;&#12497;&#12540;&#12496;&#12452;&#12470;&#12540;(3D&#12450;&#12475;&#12483;&#12488;)', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:40', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (100, 'ja', '2D Assets', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:41', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (101, 'ja', 'Render Log', '&#12524;&#12531;&#12480;&#12540;&#12539;&#12525;&#12464;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:42', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (102, 'ja', 'Asset Libraries', '&#12450;&#12475;&#12483;&#12488;&#12539;&#12521;&#12452;&#12502;&#12521;&#12522;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:43', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (103, 'ja', 'History', '&#12498;&#12473;&#12488;&#12522;&#12540;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:44', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (104, 'ja', 'Notes', '&#12494;&#12540;&#12488;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsiteasset_tab_wdg.py:45', NULL, '2007-06-16 17:00:42.406');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (39, 'ja', 'My Tactic', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:46', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (40, 'ja', 'Preproduction', '&#12503;&#12522;&#12503;&#12525;&#12480;&#12463;&#12471;&#12519;&#12531;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:47', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (41, 'ja', 'Asset Pipeline', '&#12450;&#12475;&#12483;&#12488;&#12539;&#12497;&#12452;&#12503;&#12521;&#12452;&#12531;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:48', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (42, 'ja', 'Shot Pipeline', '&#12471;&#12519;&#12483;&#12488;&#12539;&#12497;&#12452;&#12503;&#12521;&#12452;&#12531;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:49', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (43, 'ja', 'Overview', '&#12458;&#12540;&#12496;&#12540;&#12499;&#12517;&#12540;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:51', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (44, 'ja', 'Client', '&#12463;&#12521;&#12452;&#12450;&#12531;&#12488;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:52', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (45, 'ja', 'Undo', '&#20803;&#12395;&#25147;&#12377;', 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1293', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (46, 'ja', 'Admin', '&#12450;&#12489;&#12511;&#12531;', 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemain_tab_wdg.py:54', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (113, 'ja', 'Watch Lists', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:38', NULL, '2007-06-20 14:37:45.156');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (114, 'ja', 'Work Hours', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:40', NULL, '2007-06-20 14:37:45.156');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (115, 'ja', 'Clipboards', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmprodsitemy_tactic_tab_wdg.py:41', NULL, '2007-06-20 14:37:45.156');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (81, 'ja', 'Refresh', '&#20877;&#35501;&#12415;&#36796;&#12415;', 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgeticon_wdg.py:239', NULL, '2007-06-16 16:05:23.015');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (108, 'ja', 'Cancel', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetlayout_wdg.py:784', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (110, 'ja', 'Change Password', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1272', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (111, 'ja', 'change-password', NULL, 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1285', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (47, 'ja', 'Redo', '&#12420;&#12426;&#30452;&#12375;', 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1320', NULL, '2007-06-16 12:16:42.484');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (109, 'ja', 'sign-out', '&#131;T&#131;C&#131;&#147;&#131;A&#131;E&#131;g', 'C:/Program Files/Southpaw/Tactic/src/pyasmwidgetweb_wdg.py:1256', NULL, '2007-06-20 13:59:58.25');
INSERT INTO translation (id, "language", msgid, msgstr, line, "login", "timestamp") VALUES (106, 'ja', 'User', '&#131;&#134;&#129;[&#131;U&#129;[', 'C:/Program Files/Southpaw/Tactic/src/pyasmadminsitemain_tab_wdg.py:133', NULL, '2007-06-20 13:59:58.25');


--
-- PostgreSQL database dump complete
--

