

-- DEPRECATED

--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Name: notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('notification', 'id'), 17, true);


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (17, 'comment_add', 'Adding a comment to an asset', 'email', 'sthpw/note', 'bar', NULL, NULL, NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (9, 'comment_add', 'Client adding a comment', 'email', 'sthpw/note', 'bar', '<rules>
<rule group="sobject" key="context" value="client"/>
</rules>', 'Wow man.', NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (10, 'status_change', 'Changing of status to complete', 'email', 'prod/asset', 'bar', '<rules>
<rule group="command" key="to" value="Approved"/>
</rules>
', 'Yo man.  it''s done.', NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (11, 'sobject_edit', 'Assignment of task', 'email', 'sthpw/task', 'bar', '<rules>
<rule group=''sobject'' key=''assigned'' value=''.*''/>
</rules>', 'Task assigned', 'pyasm.command.TaskAssignEmailHandler');
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (13, 'status_change', 'Changing of status', 'email', 'prod/asset', 'bar', NULL, NULL, NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (12, 'asset_checkin', 'Checkin of an asset', 'email', 'prod/asset', 'bar', NULL, 'hello', NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (15, 'shot_checkin', 'Checkin of a shot', 'email', 'prod/shot', 'bar', NULL, NULL, NULL);
INSERT INTO notification (id, code, description, "type", search_type, project_code, rules, message, email_handler_cls) VALUES (14, 'shot_set_checkin', 'Checkin of a shot set', 'email', 'prod/shot', 'bar', NULL, NULL, NULL);


--
-- PostgreSQL database dump complete
--

