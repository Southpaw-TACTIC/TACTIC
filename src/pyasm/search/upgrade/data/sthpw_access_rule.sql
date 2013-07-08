
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

