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
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    search_type character varying(100) NOT NULL,
    namespace character varying(200) NOT NULL,
    description VARCHAR(MAX),
    "database" character varying(100) NOT NULL,
    table_name character varying(100) NOT NULL,
    class_name character varying(100) NOT NULL,
    title character varying(100),
    "schema" character varying(100),
    color character varying(256),
    "id_column" character varying(256),
    "default_layout" character varying(32),
    CONSTRAINT "search_object_code_idx" UNIQUE (code),
    CONSTRAINT "search_object_search_type_idx" UNIQUE (search_type)
);



CREATE TABLE project (
    id INT IDENTITY PRIMARY KEY,
    code character varying(30) NOT NULL,
    title character varying(100),
    sobject_mapping_cls character varying(100),
    dir_naming_cls character varying(200),
    code_naming_cls character varying(200),
    pipeline character varying(30),
    snapshot VARCHAR(MAX),
    "type" character varying(30),
    last_db_update timestamp ,
    description VARCHAR(MAX),
    initials character varying(30),
    file_naming_cls character varying(200),
    reg_hours numeric,
    node_naming_cls character varying(200),
    s_status character varying(30),
    status character varying(256),
    last_version_update character varying(256),
    palette character varying(256),
    category character varying(256),
    is_template boolean,
    db_resource VARCHAR(MAX),
    CONSTRAINT "project_code_idx" UNIQUE (code)
);




CREATE TABLE "login" (
    id INT IDENTITY PRIMARY KEY,
    code character varying(512),
    "login" character varying(100) NOT NULL,
    "password" character varying(255),
    "upn" character varying(100) NOT NULL,
    login_groups VARCHAR(MAX),
    first_name character varying(100),
    last_name character varying(100),
    display_name character varying(256),
    email character varying(200),
    phone_number character varying(32),
    department character varying(256),
    namespace character varying(255),
    snapshot VARCHAR(MAX),
    s_status character varying(30),
    project_code VARCHAR(MAX),
    license_type character varying(256),
    hourly_wage float,
    CONSTRAINT "login_code_idx" UNIQUE (code),
    CONSTRAINT "login_upn_idx" UNIQUE (upn)

);



CREATE TABLE "schema" (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    description VARCHAR(MAX),
    "schema" VARCHAR(MAX),
    "timestamp" timestamp  DEFAULT now(),
    "login" character varying(256),
    s_status character varying(30),
    CONSTRAINT "schema_code_idx" UNIQUE (code)
);




CREATE TABLE "trigger" (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    class_name character varying(256),
    script_path character varying(256),
    description VARCHAR(MAX),
    event character varying(256),
    mode character varying(256),
    project_code character varying(256),
    s_status character varying(256),
    process varchar(256),
    CONSTRAINT "trigger_code_idx" UNIQUE (code)
);



CREATE TABLE notification (
    id INT IDENTITY PRIMARY KEY,
    code character varying(30),
    event character varying(256),
    listen_event character varying(256),
    data VARCHAR(MAX),
    description VARCHAR(MAX),
    process varchar(256),
    "type" character varying(30) NOT NULL,
    search_type character varying(100),
    project_code character varying(30),
    rules VARCHAR(MAX),
    subject VARCHAR(MAX),
    message VARCHAR(MAX),
    email_handler_cls character varying(200),
    mail_to VARCHAR(MAX),
    mail_cc VARCHAR(MAX),
    mail_bcc VARCHAR(MAX),
    s_status character varying(30),
    title varchar(256),
    CONSTRAINT "notification_code_idx" UNIQUE (code)
);




-- minimal data required


INSERT INTO project (code, title, type) VALUES ('admin', 'Tactic','sthpw');
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
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/notification', 'sthpw/notification', 'sthpw', 'Different types of Notification', 'sthpw', 'notification', 'pyasm.biz.Notification', 'Notification', 'public');



