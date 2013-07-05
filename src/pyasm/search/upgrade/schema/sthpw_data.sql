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
-- Name: search_object_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('search_object_id_seq', 128, true);


--
-- Data for Name: search_object; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (1, 'sthpw/annotation', 'sthpw', 'Image Annotations', 'sthpw', 'annotation', 'pyasm.search.search.SObject', 'Image Annotations', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (2, 'sthpw/retire_log', 'sthpw', 'Retire SObject log', 'sthpw', 'retire_log', 'pyasm.search.RetireLog', 'Retire SObject log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (3, 'sthpw/login_in_group', 'sthpw', 'Users in groups', 'sthpw', 'login_in_group', 'pyasm.security.LoginInGroup', 'Users in groups', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (4, 'sthpw/exception_log', 'sthpw', 'Exception Log', 'sthpw', 'exception_log', 'pyasm.search.SObject', 'Exception Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (5, 'prod/sequence_instance', 'prod', 'Sequence Instance', '{project}', 'sequence_instance', 'pyasm.prod.biz.SequenceInstance', 'Sequence Instance', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (6, 'sthpw/file_access', 'sthpw', 'File Access Log', 'sthpw', 'file_access', 'pyasm.biz.FileAccess', 'File Access Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (7, 'sthpw/repo', 'sthpw', 'Repository List', 'sthpw', 'repo', 'pyasm.search.SObject', 'Repository List', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (8, 'sthpw/queue', 'sthpw', 'Tactic Dispatcher', 'sthpw', 'queue', 'pyasm.search.SObject', 'Tactic Dispatcher', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (10, 'sthpw/project', 'sthpw', 'Projects', 'sthpw', 'project', 'pyasm.biz.Project', 'Projects', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (11, 'sthpw/task', 'sthpw', 'Tasks', 'sthpw', 'task', 'pyasm.biz.Task', 'Tasks', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (12, 'sthpw/sobject_config', 'sthpw', 'SObject Config Data', 'sthpw', 'sobject_config', 'pyasm.search.SObjectDbConfig', 'SObject Config Data', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (14, 'sthpw/transaction_state', 'sthpw', 'XMLRPC State', 'sthpw', 'transaction_state', 'pyasm.search.TransactionState', 'transaction_state', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (16, 'sthpw/milestone', 'sthpw', 'Project Milestones', 'sthpw', 'milestone', 'pyasm.biz.Milestone', 'Project Milestones', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (17, 'prod/layer', 'prod', 'Layers', '{project}', '{public}.layer', 'pyasm.prod.biz.Layer', 'Layers', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (18, 'sthpw/schema', 'sthpw', 'Schema', 'sthpw', 'schema', 'pyasm.biz.Schema', 'Schema', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (19, 'prod/shot_texture', 'prod', 'Shot Texture maps', '{project}', '{public}.shot_texture', 'pyasm.prod.biz.ShotTexture', 'Shot Texture maps', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (20, 'prod/storyboard', 'prod', 'Storyboard', '{project}', '{public}.storyboard', 'pyasm.search.SObject', 'Storyboard', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (21, 'prod/episode', 'prod', 'Episode', '{project}', '{public}.episode', 'pyasm.prod.biz.Episode', 'Episode', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (22, 'prod/script', 'prod', 'Script', '{project}', '{public}.script', 'pyasm.search.SObject', 'Script', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (23, 'prod/asset_type', 'prod', 'Asset Type', '{project}', '{public}.asset_type', 'pyasm.search.SObject', 'Asset Type', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (24, 'prod/asset_library', 'prod', 'Asset Library Types', '{project}', '{public}.asset_library', 'pyasm.prod.biz.AssetLibrary', 'Asset Library Types', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (25, 'prod/node_data', 'prod', 'Maya Node Data', '{project}', 'node_data', 'pyasm.search.SObject', 'Maya Node Data', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (26, 'prod/texture_source', 'prod', 'Texture Source', '{project}', 'texture_source', 'pyasm.prod.biz.TextureSource', 'Texture Source', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (27, 'prod/leica', 'prod', 'Leica', '{project}', 'leica', 'pyasm.search.SObject', 'Leica', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (28, 'prod/render', 'prod', 'Renders', '{project}', 'render', 'pyasm.prod.biz.Render', 'Renders', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (36, 'prod/art_reference', 'prod', 'Reference Images', '{project}', 'art_reference', 'pyasm.search.SObject', 'Reference Images', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (37, 'prod/layer_instance', 'prod', 'An instance of an layer in a shot', '{project}', '{public}.layer_instance', 'pyasm.prod.biz.LayerInstance', 'An instance of an layer in a shot', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (38, 'prod/bin', 'prod', 'Bin for submissions', '{project}', 'bin', 'pyasm.prod.biz.Bin', 'Bin for submissions', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (39, 'prod/submission_in_bin', 'prod', 'Submissions in Bins', '{project}', 'submission_in_bin', 'pyasm.prod.biz.SubmissionInBin', 'Submissions in Bins', NULL);

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (41, 'prod/camera', 'prod', 'Camera Information', '{project}', 'camera', 'pyasm.search.SObject', 'Camera Information', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (45, 'game/texture', 'game', 'Game Texture', '{project}', 'texture', 'pyasm.search.SObject', 'Game Texture', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (46, 'game/asset', 'game', 'Game Asset', '{project}', 'asset', 'pyasm.search.SObject', 'Game Asset', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (47, 'game/level', 'game', 'Game Level', '{project}', 'level', 'pyasm.search.SObject', 'Game Level', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (48, 'game/level_instance', 'game', 'Game Level Instance', '{project}', 'instance', 'pyasm.search.SObject', 'Game Level Instance', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (49, 'game/art_reference', 'game', 'Reference Images', '{project}', 'art_reference', 'pyasm.search.SObject', 'Reference Images', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (50, 'prod/asset', 'prod', 'The base atomic entity that can exist shot', '{project}', '{public}.asset', 'pyasm.prod.biz.Asset', '3D Asset', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (51, 'prod/sequence', 'prod', 'A list of shots that are grouped together', '{project}', '{public}.sequence', 'pyasm.prod.biz.Sequence', 'Sequence', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (52, 'prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (53, 'prod/shot', 'prod', 'A camera cut', '{project}', '{public}.shot', 'pyasm.prod.biz.Shot', 'Shot', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (54, 'prod/shot_instance', 'prod', 'An instance of an asset in a shot', '{project}', '{public}.instance', 'pyasm.prod.biz.ShotInstance', 'Shot Instance', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (55, 'prod/submission', 'prod', 'Submission of quicktime, media files for an asset', '{project}', 'submission', 'pyasm.prod.biz.Submission', 'Submission', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (57, 'prod/render_stage', 'prod', 'Stages for specfic assets', '{project}', '{public}.render_stage', 'pyasm.search.SObject', 'Render Stage', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (58, 'sthpw/command_log', 'sthpw', 'Historical log of all of the commands executed', 'sthpw', 'command_log', 'pyasm.command.CommandLog', 'Command Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (59, 'sthpw/file', 'sthpw', 'A record of all files that are tracked', 'sthpw', 'file', 'pyasm.biz.file.File', 'File', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (60, 'sthpw/login_group', 'sthpw', 'List of groups that user belong to', 'sthpw', 'login_group', 'pyasm.security.LoginGroup', 'Groups', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (61, 'sthpw/note', 'sthpw', 'Notes', 'sthpw', 'note', 'pyasm.biz.Note', 'Notes', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (62, 'sthpw/pipeline', 'sthpw', 'List of piplines available for sobjects', 'sthpw', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (63, 'sthpw/status_log', 'sthpw', 'Log of status changes', 'sthpw', 'status_log', 'pyasm.search.SObject', 'Status Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (64, 'sthpw/notification', 'sthpw', 'Different types of Notification', 'sthpw', 'notification', 'pyasm.biz.Notification', 'Notification', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (65, 'sthpw/group_notification', 'sthpw', 'Associate one of more kinds of notification with groups', 'sthpw', 'group_notification', 'pyasm.biz.GroupNotification', 'Group Notification', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (66, 'sthpw/snapshot', 'sthpw', 'All versions of snapshots of assets', 'sthpw', 'snapshot', 'pyasm.biz.Snapshot', 'Snapshot', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (67, 'sthpw/ticket', 'sthpw', 'Valid login tickets to enter the system', 'sthpw', 'ticket', 'pyasm.security.Ticket', 'Ticket', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (68, 'sthpw/search_object', 'sthpw', 'List of all the search objects', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (69, 'sthpw/wdg_settings', 'sthpw', 'Persistent store for widgets to remember user settings', 'sthpw', 'wdg_settings', 'pyasm.web.WidgetSettings', 'Widget Settings', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (70, 'sthpw/transaction_log', 'sthpw', NULL, 'sthpw', 'transaction_log', 'pyasm.search.TransactionLog', 'Transaction Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (71, 'sthpw/trigger_in_command', 'sthpw', 'Triggers contained in Command', 'sthpw', 'trigger_in_command', 'pyasm.biz.TriggerInCommand', 'Command Triggers', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (72, 'sthpw/sobject_log', 'sthpw', 'Log of actions on an sobject', 'sthpw', 'sobject_log', 'pyasm.search.SObject', 'SObject Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (73, 'sthpw/project_type', 'sthpw', 'Project Type', 'sthpw', 'project_type', 'pyasm.biz.ProjectType', 'Project Type', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (74, 'sthpw/pref_setting', 'sthpw', 'Preference Setting', 'sthpw', '{public}.pref_setting', 'pyasm.biz.PrefSetting', 'Pref Setting', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (75, 'sthpw/access_rule', 'sthpw', 'Access Rules', 'sthpw', '{public}.access_rule', 'pyasm.security.AccessRule', 'Access Rule', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (76, 'sthpw/access_rule_in_group', 'sthpw', 'Access Rules In Group', 'sthpw', '{public}.access_rule_in_group', 'pyasm.security.AccessRuleInGroup', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (77, 'sthpw/clipboard', 'sthpw', 'Clipboard', 'sthpw', '{public}.clipboard', 'pyasm.biz.Clipboard', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (78, 'sthpw/pref_list', 'sthpw', 'Preferences List', 'sthpw', '{public}.pref_list', 'pyasm.biz.PrefList', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (79, 'sthpw/translation', 'sthpw', 'Locale Translations', 'sthpw', '{public}.translation', 'pyasm.search.SObject', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (81, 'sthpw/notification_log', 'sthpw', 'Notification Log', 'sthpw', '{public}.notification_log', 'pyasm.search.SObject', 'Notification Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (82, 'sthpw/notification_login', 'sthpw', 'Notification Login', 'sthpw', '{public}.notification_login', 'pyasm.search.SObject', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (83, 'sthpw/timecard', 'sthpw', 'Timecard Registration', 'sthpw', 'timecard', 'pyasm.search.SObject', 'Timecard', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (85, 'sthpw/connection', 'sthpw', 'Connections', 'sthpw', 'connection', 'pyasm.biz.SObjectConnection', 'Connections', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (86, 'prod/cut_sequence', 'prod', 'Cut Sequences', '{project}', 'cut_sequence', 'pyasm.prod.biz.CutSequence', 'Cut Sequences', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (87, 'prod/naming', 'prod', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (88, 'sthpw/remote_repo', 'sthpw', 'Remote Repositories', 'sthpw', 'remote_repo', 'pyasm.biz.RemoteRepo', 'Remote Repositories', NULL);
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (89, 'sthpw/widget_extend', 'sthpw', 'Extend Widget', 'sthpw', 'widget_extend', 'pyasm.search.SObject', 'widget_extend', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (90, 'prod/plate', 'prod', 'Production Plates', '{project}', 'plate', 'pyasm.search.SObject', 'Production plates', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (91, 'sthpw/search_type', 'sthpw', 'List of all the search objects', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (92, 'sthpw/snapshot_type', 'sthpw', 'Snapshot Type', 'sthpw', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (93, 'game/beat', 'game', 'Beat', '{project}', 'beat', 'pyasm.search.SObject', 'Beat', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (94, 'game/take', 'game', 'Take', '{project}', 'take', 'pyasm.search.SObject', 'Take', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (95, 'sthpw/widget_config', 'sthpw', 'Widget Config Data', 'sthpw', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config Data', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (96, 'sthpw/debug_log', 'sthpw', 'Debug Log', 'sthpw', 'debug_log', 'pyasm.biz.DebugLog', 'Debug Log', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (97, 'prod/custom_property', 'sthpw', 'Custom Property', '{project}', 'custom_property', 'pyasm.biz.CustomProperty', 'Custom Property', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (98, 'unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (99, 'unittest/city', 'unittest', 'Unittest City', 'unittest', 'city', 'pyasm.search.SObject', 'Unittest City', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (100, 'unittest/country', 'unittest', 'Unittest Country', 'unittest', 'country', 'pyasm.search.SObject', 'Unittest Country', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (101, 'prod/composite', 'prod', 'Composites', '{project}', '{public}.composite', 'pyasm.prod.biz.Composite', 'Composites', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (102, 'prod/texture', 'prod', 'Textures', '{project}', '{public}.texture', 'pyasm.prod.biz.Texture', 'Textures', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (103, 'sthpw/login', 'sthpw', 'List of users', 'sthpw', 'login', 'pyasm.security.Login', 'Users', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (104, 'sthpw/trigger', 'sthpw', 'Triggers', 'sthpw', 'trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (105, 'prod/snapshot_type', 'prod', 'Snapshot Type', '{project}', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (106, 'prod/render_policy', 'prod', 'Render Policy', '{project}', 'render_policy', 'pyasm.prod.biz.RenderPolicy', 'Render Policy', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (108, 'config/widget_config', 'config', 'Widget Config', '{project}', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (109, 'config/custom_script', 'config', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (110, 'config/naming', 'config', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (111, 'sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');

INSERT INTO search_object (id, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (112, 'config/prod_setting', 'config', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');

INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (113, 'config/client_trigger', 'config', 'Client Trigger', '{project}', 'spt_client_trigger', 'pyasm.search.SObject', 'Client Trigger', 'public'); 

INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (114, 'config/url', 'config', 'Custom URL', '{project}', 'spt_url', 'pyasm.search.SObject', 'Custom URL', 'public'); 


INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (115, 'config/plugin', 'config', 'Plugin', '{project}', 'spt_plugin', 'pyasm.search.SObject', 'Plugin', 'public'); 

INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (116, 'config/trigger', 'config', 'Triggers', '{project}', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public');

INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (117, 'config/process', 'config', 'Processes', '{project}', 'spt_process', 'pyasm.search.SObject', 'Processes', 'public');

INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (118, 'sthpw/work_hour', 'sthpw', 'Work Hours', 'sthpw', 'work_hour', 'pyasm.biz.WorkHour', 'Work Hours', 'public');

INSERT INTO search_object ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (119, 'sthpw/custom_script', 'sthpw', 'Site Custom Script', 'sthpw', 'custom_script', 'pyasm.search.SObject', 'Global Custom Script', 'public');

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
-- Name: pref_list_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pref_list_id_seq', 10, true);


--
-- Data for Name: pref_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (1, 'skin', 'These skins determine the look and feel of  TACTIC.', 'classic|dark|light|lightdark', 'sequence', 'general', 'Tactic Skins');
INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (2, 'language', 'The various language localizations', 'en_US|ja|nl', 'sequence', 'general', 'Language');
INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (3, 'thumb_multiplier', 'Determines the size multiplier of all thumbnail images', '1|2|0.5', 'sequence', 'general', 'Thumb Size');
INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (4, 'debug', 'Determines whether to show debug information', 'false|true', 'sequence', 'general', 'Debug');
-- INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (5, 'select_filter', 'Determines whether to show some filters as multi-select', 'single|multi', 'sequence', 'general', 'Select Filter');
--INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (6, 'use_java_maya', 'Determines whether to use the java applet Maya connector', 'false|true', 'sequence', 'general', 'Java Maya Connector');
INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (7, 'js_logging_level','Determines logging level used by Web Client Output Console Pop-up','CRITICAL|ERROR|WARNING|INFO|DEBUG','sequence','general','Web Client Logging Level');
INSERT INTO pref_list (id, "key", description, options, "type", category, title) VALUES (8, 'quick_text','Quick text for Note Sheet','','string','general','Quick Text');


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
-- Name: pipeline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pipeline_id_seq', 5, true);


--
-- Data for Name: pipeline; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO pipeline (id, code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES (1, 'default', '<pipeline type="serial">
  <process name="No Pipeline" completion="0"/>
</pipeline>', '2007-06-27 19:16:02.697673', NULL, NULL, NULL, NULL);
INSERT INTO pipeline (id, code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES (2, 'task', '<?xml version="1.0" encoding="UTF-8"?>
<pipeline type="serial">
  <process completion="0" color="grey" name="Assignment"/>
  <process completion="10" color="grey" name="Pending"/>
  <process completion="20" color="blue" name="In Progress"/>
  <process completion="20" name="Waiting"/>
  <process completion="30" color="red" name="Need Assistance"/>
  <process completion="80" name="Review"/>
  <process completion="100" color="green" name="Approved"/>
  <connect to="Review" from="Need Assistance"/>
  <connect to="In Progress" from="Pending"/>
  <connect to="Pending" from="Assignment"/>
  <connect to="Need Assistance" from="Waiting"/>
  <connect to="Waiting" from="In Progress"/>
  <connect to="Approved" from="Review"/>
</pipeline>', '2007-06-27 19:16:02.729832', 'sthpw/task', NULL, NULL, NULL);
INSERT INTO pipeline (id, code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES (3, 'model', '<?xml version="1.0" encoding="UTF-8"?>  
<pipeline type="serial">  
  <process name="model"/>  
  <process name="texture"/>  
  <process name="shader"/>  
  <process name="rig"/>  
  <connect to="texture" from="model" context="model"/>  
  <connect to="shader" from="texture" context="texture"/>  
  <connect to="shot/layout" from="rig" context="rig"/> 
  <connect to="rig" from="texture" context="texture"/>  
  <connect to="shot/lighting" from="shader"/>  
</pipeline>', '2007-06-27 19:16:02.733281', 'prod/asset', NULL, NULL, NULL);
INSERT INTO pipeline (id, code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES (4, 'shot', '<?xml version="1.0" encoding="UTF-8"?> 
<pipeline type="parallel"> 
  <process name="layout"/> 
  <process name="anim"/> 
  <process name="char_final"/> 
  <process name="effects"/> 
  <process name="lighting"/> 
  <process name="compositing"/> 
  <connect to="layout" from="model/model" context="model"/>
  <connect to="layout" from="model/rig" context="rig"/> 
  <connect to="anim" from="layout"/> 
  <connect to="char_final" from="anim"/> 
  <connect to="char_final" from="model/texture" context="texture"/> 
  <connect to="effects" from="char_final"/> 
  <connect to="lighting" from="effects"/> 
  <connect to="lighting" from="char_final"/> 
  <connect to="compositing" from="lighting"/> 
</pipeline>', '2007-06-27 19:16:02.735433', 'prod/shot', NULL, NULL, NULL);


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
-- Name: project_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('project_type_id_seq', 12, true);


--
-- Data for Name: project_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "project_type" ("id", "code", "dir_naming_cls", "file_naming_cls", "code_naming_cls", "node_naming_cls", "sobject_mapping_cls", "s_status", "type", "repo_handler_cls") VALUES (3, 'custom', NULL, NULL, NULL, NULL, NULL, NULL, 'simple', NULL);
--INSERT INTO "project_type" ("id", "code", "dir_naming_cls", "file_naming_cls", "code_naming_cls", "node_naming_cls", "sobject_mapping_cls", "s_status", "type", "repo_handler_cls") VALUES (7, 'game', 'pyasm.prod.biz.ProdDirNaming', 'pyasm.prod.biz.ProdFileNaming', NULL, NULL, 'pyasm.game.biz.GameMapping', NULL, 'game', NULL);
INSERT INTO "project_type" ("id", "code", "dir_naming_cls", "file_naming_cls", "code_naming_cls", "node_naming_cls", "sobject_mapping_cls", "s_status", "type", "repo_handler_cls") VALUES (1, 'prod', 'pyasm.prod.biz.ProdDirNaming', 'pyasm.prod.biz.ProdFileNaming', '', '', '', NULL, 'prod', NULL);



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
-- Name: access_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('access_rule_id_seq', 14, true);


--
-- Data for Name: access_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (5, NULL, 'standard_user', 'Basic access for internal users', '<rules>
<rule group=''tab'' key=''My Tactic'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Tasks'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Notes'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Notifications'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Work Hours'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Clipboards'' access=''allow''/>
<rule group=''tab'' key=''My Tactic/Preferences'' access=''allow''/>
<rule group=''tab'' key=''Undo'' access=''allow''/>
</rules>
', '2008-01-21 17:41:44.301118');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (7, NULL, 'producer_tabs', 'Tabs for producers', '<rules>
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Shot Pipeline" access=''view''/>  
<rule group="tab" key="Shot Pipeline/Shot List" access=''view''/>
<rule group="tab" key="Shot Pipeline/Shot Planner" access=''view''/>
<rule group="tab" key="Asset Pipeline" access=''view''/>  
<rule group="tab" key="Asset Pipeline/Summary" access=''view''/>  
<rule group="tab" key="Overview" access=''view''/>  
<rule group="tab" key="Overview/Tasks (Assets)" access=''view''/>  
<rule group="tab" key="Overview/Tasks (Shots)" access=''view''/>  
<rule group="tab" key="Overview/Layout Summary" access=''view''/>  
<rule group="tab" key="Overview/Asset Summary" access=''view''/>  
<rule group="tab" key="Editorial" access=''view''/> 
<rule group="tab" key="Editorial/Dailies" access=''view''/> 
<rule group="tab" key="Client" access=''view''/> 
<rule group="tab" key="Client/Review" access=''view''/> 
</rules> 
', '2008-01-22 16:31:31.259716');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (10, NULL, 'model_supervisor_tabs', 'Model Supervisor Tabs', '<rules>
<rule group=''tab'' key=''Asset Pipeline/Supe (3D Assets)'' access=''allow''/>
</rules>', '2008-01-24 05:36:35.692611');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (4, NULL, 'hide_user_filter', 'Hide the User Filter', '<rules>
<rule access=''deny'' key=''UserFilterWdg'' category=''public_wdg''/>
</rules>', '2007-09-29 11:48:48.718');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (9, NULL, 'modeller_tabs', 'Modeller''s Tabs', '<rules>  
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Asset Pipeline" access=''view''/>  
<rule group="tab" key="Asset Pipeline/Artist (3D Assets)" access=''view''/>  
<rule group="tab" key="Asset Pipeline/2D Assets" access=''view''/>  
<rule group="tab" key="3D Asset" access=''view''/>  
<rule group="tab" key="Checkin" access=''view''/>  
<rule group="tab" key="Log" access=''view''/>  
</rules> 
', '2008-01-23 05:58:04.494858');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (11, NULL, 'hide_task_status', 'Hide the Complete or Approved status from the Task Status dropdown', '<rules>
        <rule access=''deny'' key=''Complete'' category=''process_select''/>
        <rule access=''deny'' key=''Approved'' category=''process_select''/>
        </rules>', '2007-10-25 18:32:37.609');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (14, NULL, 'previz_tabs', 'Previz Tabs', '<rules>  
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Preproduction" access=''view''/>  
<rule group="tab" key="Preproduction/Reference" access=''view''/> 
<rule group="tab" key="Preproduction/Scripts" access=''view''/> 
<rule group="tab" key="Preproduction/Storyboards" access=''view''/> 
<rule group="tab" key="Preproduction/Camera Data" access=''view''/> 
<rule group="tab" key="Preproduction/Notes" access=''view''/> 
<rule group="tab" key="My Tactic" access=''view''/>  
</rules> ', '2008-04-08 16:23:18.567469');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (8, NULL, 'animator_tabs', 'Animator''s Tabs', '<rules>  
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Shot Pipeline" access=''view''/>  
<rule group="tab" key="Shot Pipeline/Artist (Shots)" access=''view''/>  
<rule group="tab" key="Shot Pipeline/Layers" access=''view''/>  
<rule group="tab" key="Shot Pipeline/Composites" access=''view''/>  
</rules> 
', '2008-01-22 16:33:37.171238');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (3, NULL, 'show_user_filter', 'Right to see the User Filter', '<rules>
<rule access=''view'' key=''UserFilterWdg'' category=''secure_wdg''/>
<rule category=''prod/shot'' key=''s_status'' value=''retired'' access=''allow''/>
</rules>', '2007-05-31 12:13:03.015');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (2, NULL, 'show_user_assign_wdg', 'Right to see User Assign Widget in Supe tabs for Asset/Shot pipeline', '<rules>
<rule access=''view'' key=''UserAssignWdg'' category=''secure_wdg''/>
</rules>', '2007-10-02 18:47:06.39');
INSERT INTO access_rule (id, project_code, code, description, "rule", "timestamp") VALUES (1, NULL, 'client', 'Deny all tabs but the client tab. Allow to see the project named [sample3d]', '<rules>  
<rule group=''project'' default=''deny''/>  
<rule group=''project'' key=''sample3d'' access=''view''/>  
<rule group=''project'' key=''default'' access=''view''/>  
  
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Client" access=''view''/>  
<rule group="tab" key="Client/Review" access=''view''/>  
</rules> 
', '2007-05-29 22:50:16.937');


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
-- Name: command_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('command_id_seq', 2, true);


--
-- Data for Name: command; Type: TABLE DATA; Schema: public; Owner: postgres
--

--INSERT INTO command (id, class_name, description, notification_code, s_status) VALUES (1, 'SimpleStatusCmd', 'Command for changing statuses', 'status_changed', NULL);
--INSERT INTO command (id, class_name, description, notification_code, s_status) VALUES (2, 'CommentCmd', 'Command for adding comments', 'comment_added', NULL);


--
-- PostgreSQL database dump complete
--

