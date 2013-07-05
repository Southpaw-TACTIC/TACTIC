--# add the default user (admin)

--add sthpw project
INSERT INTO project (code, title, type) VALUES ('sthpw', 'Tactic', 'sthpw');
INSERT INTO project (code, title) VALUES ('admin', 'Tactic Admin');

--add in admin group
INSERT INTO login_group (login_group, description)
VALUES ('admin', 'Site Administration');

--add in admin user, default password 'tactic'
INSERT INTO "login" ("login", "password", first_name, last_name)
VALUES ('admin', '39195b0707436a7ecb92565bf3411ab1', 'Admin', '');

--add the admin user to the admin group
INSERT INTO login_in_group ("login", login_group) VALUES ('admin', 'admin');


--# add in the necessary triggers for email notification

--register notification
INSERT INTO notification (code, description, "type", search_type, event)
VALUES ('asset_attr_change', 'Attribute Changes For Assets', 'email', 'prod/asset', 'update|prod/asset');
INSERT INTO notification (code, description, "type", search_type, event)
VALUES ('shot_attr_change', 'Attribute Changes For Shots', 'email', 'prod/shot', 'update|prod/shot');
