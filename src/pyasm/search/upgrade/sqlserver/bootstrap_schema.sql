SET QUOTED_IDENTIFIER ON;
--
--


-- These are the miminum set of tables required for the plugin installer
-- to function.  The tables are:

-- search_object
-- project
-- login
-- trigger
-- schema
-- notification


CREATE TABLE search_object (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(100) NOT NULL,
    namespace nvarchar(200) NOT NULL,
    description nvarchar(max),
    "database" nvarchar(100) NOT NULL,
    table_name nvarchar(100) NOT NULL,
    class_name nvarchar(100) NOT NULL,
    title nvarchar(100),
    "schema" nvarchar(100),
    color nvarchar(256),
    "id_column" nvarchar(256),
    "default_layout" nvarchar(32),
    CONSTRAINT "search_object_code_idx" UNIQUE (code),
    CONSTRAINT "search_object_search_type_idx" UNIQUE (search_type)
);



CREATE TABLE project (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(30) NOT NULL,
    title nvarchar(100),
    sobject_mapping_cls nvarchar(100),
    dir_naming_cls nvarchar(200),
    code_naming_cls nvarchar(200),
    pipeline nvarchar(30),
    snapshot nvarchar(max),
    "type" nvarchar(30),
    last_db_update datetime2(6),
    description nvarchar(max),
    initials nvarchar(30),
    file_naming_cls nvarchar(200),
    reg_hours numeric,
    node_naming_cls nvarchar(200),
    s_status nvarchar(30),
    status nvarchar(256),
    last_version_update nvarchar(256),
    palette nvarchar(256),
    category nvarchar(256),
    is_template BIT,
    db_resource nvarchar(max),
    CONSTRAINT "project_code_idx" UNIQUE (code)
);




CREATE TABLE "login" (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(512),
    "login" nvarchar(100) NOT NULL,
    "password" nvarchar(255),
    login_groups nvarchar(max),
    first_name nvarchar(100),
    last_name nvarchar(100),
    display_name nvarchar(256),
    email nvarchar(200),
    phone_number nvarchar(32),
    department nvarchar(256),
    namespace nvarchar(255),
    snapshot nvarchar(max),
    s_status nvarchar(30),
    project_code nvarchar(max),
    license_type nvarchar(256),
    hourly_wage float,
    CONSTRAINT "login_code_idx" UNIQUE (code)
);



CREATE TABLE "schema" (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    description nvarchar(max),
    "schema" nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    "login" nvarchar(256),
    s_status nvarchar(30),
    CONSTRAINT "schema_code_idx" UNIQUE (code)
);




CREATE TABLE "trigger" (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    class_name nvarchar(256),
    script_path nvarchar(256),
    description nvarchar(max),
    event nvarchar(256),
    mode nvarchar(256),
    project_code nvarchar(256),
    s_status nvarchar(256),
    process nvarchar(256),
    CONSTRAINT "trigger_code_idx" UNIQUE (code)
);



CREATE TABLE notification (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(30),
    event nvarchar(256),
    listen_event nvarchar(256),
    data nvarchar(max),
    description nvarchar(max),
    process nvarchar(256),
    "type" nvarchar(30) NOT NULL,
    search_type nvarchar(100),
    project_code nvarchar(30),
    rules nvarchar(max),
    subject nvarchar(max),
    message nvarchar(max),
    email_handler_cls nvarchar(200),
    mail_to nvarchar(max),
    mail_cc nvarchar(max),
    mail_bcc nvarchar(max),
    s_status nvarchar(30),
    title nvarchar(256),
    CONSTRAINT "notification_code_idx" UNIQUE (code)
);




-- minimal data required


INSERT INTO project (code, title,) VALUES ('admin', 'Tactic','sthpw');
INSERT INTO project (code, title) VALUES ('sthpw', 'Tactic Admin');

-- Project
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/project', 'sthpw/project', 'sthpw', 'Projects', 'sthpw', 'project', 'pyasm.biz.Project', 'Projects', NULL);
-- Schema
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/schema', 'sthpw/schema', 'sthpw', 'Schema', 'sthpw', 'schema', 'pyasm.biz.Schema', 'Schema', 'public');
-- Login
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/login', 'sthpw/login', 'sthpw', 'List of users', 'sthpw', 'login', 'pyasm.security.Login', 'Users', 'public');
-- Search Types
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/search_object', 'sthpw/search_object', 'sthpw', 'Search Types', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
-- Trigger
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/trigger', 'sthpw/trigger', 'sthpw', 'Triggers', 'sthpw', 'trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public');
-- Notification
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/notification', 'sthpw/notification', 'sthpw', 'Differents of Notification', 'sthpw', 'notification', 'pyasm.biz.Notification', 'Notification', 'public');



