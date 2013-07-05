--
--

CREATE TABLE db_resource (
    id serial PRIMARY KEY,
    code character varying(256),
    host text,
    port integer,
    vendor character varying(256),
    login character varying(256),
    password text,
    CONSTRAINT "db_resource_code_idx" UNIQUE (code)
);

CREATE TABLE access_log (
    id serial PRIMARY KEY,
    code character varying(256),
    url character varying(256),
    data character varying(256),
    "start_time" timestamp without time zone,
    "end_time" timestamp without time zone,
    duration double precision,
    CONSTRAINT "access_log_code_idx" UNIQUE (code)
);


CREATE TABLE command_log (
    id serial PRIMARY KEY,
    code character varying(256),
    class_name character varying(100) NOT NULL,
    paramaters character varying(256),
    login character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT "command_log_code_idx" UNIQUE (code)
);


CREATE TABLE connection (
    id serial PRIMARY KEY,
    code character varying(256),
    context character varying(60),
    project_code character varying(30),
    src_search_type character varying(200),
    src_search_id integer,
    dst_search_type character varying(200),
    dst_search_id integer,
    login character varying(30),
    "timestamp" timestamp without time zone DEFAULT now()
);


CREATE TABLE file_access (
    id serial PRIMARY KEY,
    code character varying(256),
    file_code integer NOT NULL,
    login character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);



CREATE TABLE queue (
    id serial PRIMARY KEY,
    code character varying(256),
    queue character varying(30) NOT NULL,
    priority character varying(10) NOT NULL,
    description character varying(256),
    state character varying(30) NOT NULL DEFAULT 'pending',
    login character varying(30) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    command character varying(200) NOT NULL,
    serialized character varying(256) NOT NULL,
    s_status character varying(30),
    project_code character varying(100),
    search_id integer,
    search_type character varying(100),
    dispatcher_id integer,
    policy_code character varying(30),
    host character varying(256)
);


CREATE TABLE repo (
    id serial PRIMARY KEY,
    code character varying(256) NOT NULL,
    description character varying(256) NOT NULL,
    handler character varying(100) NOT NULL,
    web_dir character varying(256) NOT NULL,
    lib_dir character varying(256) NOT NULL
);


CREATE TABLE snapshot_type (
    id serial PRIMARY KEY,
    code character varying(256),
    pipeline_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    login character varying(256),
    s_status character varying(256),
    relpath character varying(256),
    project_code character varying(256),
    subcontext character varying(256),
    snapshot_flavor character varying(256),
    relfile character varying(256),
    CONSTRAINT "snapshot_type_code_unique" UNIQUE (code)
);


CREATE TABLE special_day (
    id serial PRIMARY KEY,
    code character varying(256),
    week integer,
    mon float, 
    tue float, 
    wed float, 
    thu float, 
    fri float, 
    sat float, 
    sun float, 
    year integer, 
    login character varying(256),
    description character varying(256),
    "type" character varying(256),
    project_code character varying(256)
);


CREATE TABLE custom_property (
    id serial PRIMARY KEY,
    code character varying(256),
    search_type character varying(256),
    name character varying(256),
    description character varying(256),
    login character varying(256)
);


CREATE TABLE pref_list (
    id serial PRIMARY KEY,
    code character varying(256),
    "key" character varying(256),
    description character varying(256),
    options character varying(256),
    "type" character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    title character varying(256),
    CONSTRAINT "pref_list_key_idx" UNIQUE ("key")
);



CREATE TABLE retire_log (
    id serial PRIMARY KEY,
    code character varying(256),
    search_type character varying(100),
    search_id character varying(100),
    login character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    CONSTRAINT "retire_log_code_idx" UNIQUE (code)
);


CREATE TABLE translation (
    id serial PRIMARY KEY,
    code character varying(256),
    language character varying(256),
    msgid character varying(256),
    msgstr character varying(256),
    line character varying(256),
    login character varying(256),
    "timestamp" timestamp without time zone DEFAULT now()
);


CREATE TABLE project_type (
    id serial PRIMARY KEY,
    code character varying(30),
    dir_naming_cls character varying(200),
    file_naming_cls character varying(200),
    code_naming_cls character varying(200),
    node_naming_cls character varying(200),
    sobject_mapping_cls character varying(200),
    s_status character varying(32),
    "type" character varying(100) NOT NULL,
    repo_handler_cls character varying(200),
    CONSTRAINT "project_type_code_idx" UNIQUE (code)
);



CREATE TABLE login_group (
    id serial PRIMARY KEY,
    code character varying(256),
    login_group character varying(100) NOT NULL,
    sub_groups text,
    access_rules text,
    redirect_url text,
    namespace character varying(255),
    description text,
    project_code text,
    s_status character varying(256),
    start_link text,
    access_level varchar(32),
    CONSTRAINT "login_group_code_idx" UNIQUE (code)
);



CREATE TABLE login_in_group (
    id serial PRIMARY KEY,
    code character varying(256),
    "login" character varying(100) NOT NULL,
    login_group character varying(100) NOT NULL
);



CREATE TABLE ticket (
    id serial PRIMARY KEY,
    code character varying(256),
    ticket character varying(100) NOT NULL,
    "login" character varying(100),
    "timestamp" timestamp with time zone DEFAULT now(),
    expiry timestamp without time zone,
    category character varying(256),
    CONSTRAINT "ticket_code_idx" UNIQUE (code),
    CONSTRAINT "ticket_ticket_idx" UNIQUE (ticket)
);




CREATE TABLE pipeline (
    id serial PRIMARY KEY,
    code character varying(256),
    pipeline text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    search_type character varying(100),
    project_code character varying(30),
    description text,
    color varchar(256),
    s_status character varying(30),
    autocreate_tasks boolean,
    CONSTRAINT "pipeline_code_idx" UNIQUE (code)
);



-- FIXME: Is this needed anymore?
-- FIXME: notification_id will be deprecated in 4.0
CREATE TABLE group_notification (
    id serial PRIMARY KEY,
    login_group character varying(100) NOT NULL,
    notification_id integer NOT NULL
);
CREATE TABLE notification_login (
    id serial PRIMARY KEY,
    notification_log_id integer,
    "login" character varying(256),
    "type" character varying(256),
    project_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now()
);



CREATE TABLE notification_log (
    id serial PRIMARY KEY,
    project_code character varying(256),
    "login" character varying(256),
    command_cls character varying(256),
    subject text,
    message text,
    "timestamp" timestamp without time zone DEFAULT now()
);


CREATE TABLE snapshot (
    id serial PRIMARY KEY,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    column_name character varying(100) NOT NULL,
    snapshot text NOT NULL,
    description text,
    process varchar(256),
    "login" character varying(100) NOT NULL,
    "lock_login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    lock_date timestamp,
    context character varying(256),
    version integer,
    s_status character varying(30),
    snapshot_type character varying(30),
    code character varying(30),
    repo character varying(30),
    is_current boolean,
    label character varying(100),
    revision smallint,
    level_type character varying(256),
    level_id integer,
    metadata text,
    is_latest boolean,
    status character varying(256),
    project_code character varying(256),
    search_code character varying(256),
    is_synced boolean,
    CONSTRAINT "snapshot_code_idx" UNIQUE (code)
);

CREATE TABLE file (
    id serial PRIMARY KEY,
    file_name character varying(512) NOT NULL,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    st_size bigint,
    file_range text,
    code character varying(30),
    snapshot_code character varying(30),
    project_code character varying(100),
    md5 character varying(32),
    checkin_dir text,
    source_path text,
    relative_dir text,
    "type" character varying(256),
    base_type character varying(256),
    metadata text,
    metadata_search text, 
    repo_type varchar(256), 
    "base_dir_alias" character varying(256),
    
    CONSTRAINT "file_code_idx" UNIQUE (code)
);



-- NOTE: is this really needed anymore?  Check-in is dependent on it!
CREATE TABLE remote_repo (
    id serial PRIMARY KEY,
    code character varying(30),
    ip_address character varying(30),
    ip_mask character varying(30),
    repo_base_dir character varying(200),
    sandbox_base_dir character varying(200),
    "login" character varying(100),
    CONSTRAINT "remote_repo_code_idx" UNIQUE (code)
);




CREATE TABLE milestone (
    id serial PRIMARY KEY,
    code character varying(256),
    project_code character varying(256),
    description text,
    due_date timestamp without time zone,
    CONSTRAINT "milestone_code_idx" UNIQUE (code)
);




-- NOTE: file name is deleted
CREATE TABLE task (
    id serial PRIMARY KEY,
    -- file_name character varying(512) NOT NULL,
    assigned character varying(100),
    description text,
    status text,
    discussion text,
    bid_start_date timestamp without time zone,
    bid_end_date timestamp without time zone,
    bid_duration double precision,
    actual_start_date timestamp without time zone,
    actual_end_date timestamp without time zone,
    search_type character varying(100),
    search_id integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(30),
    priority smallint,
    process character varying(256),
    context character varying(256),
    milestone_code character varying(200),
    pipeline_code character varying(256),
    parent_id integer,
    sort_order smallint,
    depend_id integer,
    project_code character varying(100),
    supervisor character varying(100),
    code character varying(256),
    login character varying(256),
    completion float,
    CONSTRAINT "task_code_idx" UNIQUE (code)
);


CREATE TABLE note (
    id serial PRIMARY KEY,
    code character varying(256),
    project_code character varying(30),
    search_type character varying(200),
    search_id integer,
    "login" character varying(30),
    context character varying(60),
    "timestamp" timestamp without time zone DEFAULT now(),
    note text,
    title character varying(1024),
    parent_id bigint,
    status character varying(256),
    label character varying(256),
    process character varying(60),
    "sort_order" integer,
    "access" character varying(256),
    CONSTRAINT "note_code_idx" UNIQUE (code)
);




CREATE TABLE pref_setting (
    id serial PRIMARY KEY,
    project_code character varying(256),
    "login" character varying(256),
    "key" character varying(256),
    value text,
    "timestamp" timestamp without time zone DEFAULT now()
);


CREATE TABLE wdg_settings (
    id serial PRIMARY KEY,
    "key" character varying(255) NOT NULL,
    "login" character varying(100) NOT NULL,
    data text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    project_code character varying(30)
);



CREATE TABLE clipboard (
    id serial PRIMARY KEY,
    project_code character varying(256),
    "login" character varying(256),
    search_type character varying(256),
    search_id integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    category character varying(256)
);






CREATE TABLE exception_log (
    id serial PRIMARY KEY,
    "class" character varying(100),
    message text,
    stack_trace text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);




CREATE TABLE transaction_log (
    id serial PRIMARY KEY,
    "code" character varying(256),
    "transaction" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    description text,
    command character varying(100),
    title text,
    "type" character varying(30),
    namespace character varying(100),
    CONSTRAINT "transaction_log_code_idx" UNIQUE (code)
);

CREATE INDEX "transaction_log_timestamp_idx" ON transaction_log ("timestamp");
CREATE INDEX "transaction_log_idx" ON transaction_log (login, namespace, "type");





-- FIXME: is this really needed???
CREATE TABLE transaction_state (
    id serial PRIMARY KEY,
    ticket character varying(100),
    "timestamp" timestamp without time zone DEFAULT now(),
    data text,
    CONSTRAINT "transaction_state_ticket_idx" UNIQUE (ticket)
);




CREATE TABLE sobject_log (
    id serial PRIMARY KEY,
    search_type character varying(100) NOT NULL,
    search_id integer NOT NULL,
    data text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    transaction_log_id integer
);


CREATE TABLE status_log (
    id serial PRIMARY KEY,
    search_type character varying(256) NOT NULL,
    search_id integer NOT NULL,
    status text,
    "login" character varying(256) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    to_status character varying(256),
    from_status character varying(256),
    project_code character varying(256)
);

CREATE TABLE debug_log (
    id serial PRIMARY KEY,
    category character varying(256),
    "level" character varying(256),
    message text,
    "timestamp" timestamp without time zone DEFAULT now(),
    "login" character varying(256),
    s_status character varying(30)
);



CREATE TABLE work_hour (
    id serial PRIMARY KEY,
    code character varying(256),
    project_code character varying(256),
    description text,
    category character varying(256),
    process character varying(256),
    "login" character varying(256),
    "day" timestamp without time zone,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    straight_time double precision,
    over_time double precision,
    search_type character varying(256),
    search_id integer,
    status character varying(256),
    task_code character varying(256),
    CONSTRAINT "work_hour_code_idx" UNIQUE (code)
);






-- in upgrade
CREATE TABLE cache (
    id serial PRIMARY KEY,
    "key" varchar(256),
    mtime timestamp
);


CREATE TABLE sobject_list (
    id serial PRIMARY KEY,
    code varchar(256),
    search_type varchar(256),
    search_id integer,
    keywords text,
    "timestamp" timestamp default now(),
    project_code varchar(256),
    CONSTRAINT "sobject_list_code_idx" UNIQUE (code)
);




INSERT INTO project (code) VALUES ('unittest');



-- FIXME: are thse needed anymore?
-- INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES (87, 'prod/naming', 'prod', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/db_resource', 'sthpw/db_resource', 'sthpw', 'Database Resource', 'sthpw', 'db_resource', 'pyasm.search.SObject', 'Database Resource', 'public');


INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/custom_property', 'config/custom_property', 'sthpw', 'Custom Property', '{project}', 'custom_property', 'pyasm.biz.CustomProperty', 'Custom Property', 'public');




INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/annotation', 'sthpw/annotation', 'sthpw', 'Image Annotations', 'sthpw', 'annotation', 'pyasm.search.search.SObject', 'Image Annotations', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/retire_log', 'sthpw/retire_log', 'sthpw', 'Retire SObject log', 'sthpw', 'retire_log', 'pyasm.search.RetireLog', 'Retire SObject log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/login_in_group', 'sthpw/login_in_group', 'sthpw', 'Users in groups', 'sthpw', 'login_in_group', 'pyasm.security.LoginInGroup', 'Users in groups', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/exception_log', 'sthpw/exception_log', 'sthpw', 'Exception Log', 'sthpw', 'exception_log', 'pyasm.search.SObject', 'Exception Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/file_access', 'sthpw/file_access', 'sthpw', 'File Access Log', 'sthpw', 'file_access', 'pyasm.biz.FileAccess', 'File Access Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/repo', 'sthpw/repo', 'sthpw', 'Repository List', 'sthpw', 'repo', 'pyasm.search.SObject', 'Repository List', NULL);
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/queue', 'sthpw/queue', 'sthpw', 'Tactic Dispatcher', 'sthpw', 'queue', 'pyasm.search.SObject', 'Tactic Dispatcher', NULL);
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/task', 'sthpw/task', 'sthpw', 'User Tasks', 'sthpw', 'task', 'pyasm.biz.Task', 'User Tasks', NULL);
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/sobject_config', 'sthpw/sobject_config', 'sthpw', 'SObject Config Data', 'sthpw', 'sobject_config', 'pyasm.search.SObjectDbConfig', 'SObject Config Data', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/transaction_state', 'sthpw/transaction_state', 'sthpw', 'XMLRPC State', 'sthpw', 'transaction_state', 'pyasm.search.TransactionState', 'transaction_state', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/command', 'sthpw/command', 'sthpw', 'Commands in Tactic', 'sthpw', 'command', 'pyasm.biz.CommandSObj', 'Commands in Tactic', 'public');



INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/command_log', 'sthpw/command_log', 'sthpw', 'Historical log of all of the commands executed', 'sthpw', 'command_log', 'pyasm.command.CommandLog', 'Command Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/file', 'sthpw/file', 'sthpw', 'A record of all files that are tracked', 'sthpw', 'file', 'pyasm.biz.file.File', 'File', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/login_group', 'sthpw/login_group', 'sthpw', 'List of groups that user belong to', 'sthpw', 'login_group', 'pyasm.security.LoginGroup', 'Groups', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/note', 'sthpw/note', 'sthpw', 'Notes', 'sthpw', 'note', 'pyasm.biz.Note', 'Notes', NULL);
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/pipeline', 'sthpw/pipeline', 'sthpw', 'List of piplines available for sobjects', 'sthpw', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/status_log', 'sthpw/status_log', 'sthpw', 'Log of status changes', 'sthpw', 'status_log', 'pyasm.search.SObject', 'Status Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/group_notification', 'sthpw/group_notification', 'sthpw', 'Associate one of more kinds of notification with groups', 'sthpw', 'group_notification', 'pyasm.biz.GroupNotification', 'Group Notification', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/snapshot', 'sthpw/snapshot', 'sthpw', 'All versions of snapshots of assets', 'sthpw', 'snapshot', 'pyasm.biz.Snapshot', 'Snapshot', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/ticket', 'sthpw/ticket', 'sthpw', 'Valid login tickets to enter the system', 'sthpw', 'ticket', 'pyasm.security.Ticket', 'Ticket', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/wdg_settings', 'sthpw/wdg_settings', 'sthpw', 'Persistent store for widgets to remember user settings', 'sthpw', 'wdg_settings', 'pyasm.web.WidgetSettings', 'Widget Settings', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/transaction_log', 'sthpw/transaction_log', 'sthpw', NULL, 'sthpw', 'transaction_log', 'pyasm.search.TransactionLog', 'Transaction Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/sobject_log', 'sthpw/sobject_log', 'sthpw', 'Log of actions on an sobject', 'sthpw', 'sobject_log', 'pyasm.search.SObject', 'SObject Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/project_type', 'sthpw/project_type', 'sthpw', 'Project Type', 'sthpw', 'project_type', 'pyasm.biz.ProjectType', 'Project Type', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/pref_setting', 'sthpw/pref_setting', 'sthpw', 'Preference Setting', 'sthpw', '{public}.pref_setting', 'pyasm.biz.PrefSetting', 'Pref Setting', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/access_rule', 'sthpw/access_rule', 'sthpw', 'Access Rules', 'sthpw', '{public}.access_rule', 'pyasm.security.AccessRule', 'Access Rule', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/access_rule_in_group', 'sthpw/access_rule_in_group', 'sthpw', 'Access Rules In Group', 'sthpw', '{public}.access_rule_in_group', 'pyasm.security.AccessRuleInGroup', '', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/clipboard', 'sthpw/clipboard', 'sthpw', 'Clipboard', 'sthpw', '{public}.clipboard', 'pyasm.biz.Clipboard', '', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/pref_list', 'sthpw/pref_list', 'sthpw', 'Preferences List', 'sthpw', '{public}.pref_list', 'pyasm.biz.PrefList', '', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/translation', 'sthpw/translation', 'sthpw', 'Locale Translations', 'sthpw', '{public}.translation', 'pyasm.search.SObject', '', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/notification_log', 'sthpw/notification_log', 'sthpw', 'Notification Log', 'sthpw', '{public}.notification_log', 'pyasm.search.SObject', 'Notification Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/notification_login', 'sthpw/notification_login', 'sthpw', 'Notification Login', 'sthpw', '{public}.notification_login', 'pyasm.search.SObject', '', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/connection', 'sthpw/connection', 'sthpw', 'Connections', 'sthpw', 'connection', 'pyasm.biz.SObjectConnection', 'Connections', NULL);





INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/remote_repo', 'sthpw/remote_repo', 'sthpw', 'Remote Repositories', 'sthpw', 'remote_repo', 'pyasm.biz.RemoteRepo', 'Remote Repositories', NULL);
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/widget_extend', 'sthpw/widget_extend', 'sthpw', 'Extend Widget', 'sthpw', 'widget_extend', 'pyasm.search.SObject', 'widget_extend', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/snapshot_type', 'sthpw/snapshot_type', 'sthpw', 'Snapshot Type', 'sthpw', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/widget_config', 'sthpw/widget_config', 'sthpw', 'Widget Config Data', 'sthpw', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config Data', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/debug_log', 'sthpw/debug_log', 'sthpw', 'Debug Log', 'sthpw', 'debug_log', 'pyasm.biz.DebugLog', 'Debug Log', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('unittest/person', 'unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('unittest/city', 'unittest/city', 'unittest', 'Unittest City', 'unittest', 'city', 'pyasm.search.SObject', 'Unittest City', 'public');
INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('unittest/country', 'unittest/country', 'unittest', 'Unittest Country', 'unittest', 'country', 'pyasm.search.SObject', 'Unittest Country', 'public');



INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/widget_config', 'config/widget_config', 'config', 'Widget Config', '{project}', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/custom_script', 'config/custom_script', 'config', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/naming', 'config/naming', 'config', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/cache', 'sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/prod_setting', 'config/prod_setting', 'config', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/client_trigger', 'config/client_trigger', 'config', 'Client Trigger', '{project}', 'spt_client_trigger', 'pyasm.search.SObject', 'Client Trigger', 'public'); 

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/url', 'config/url', 'config', 'Custom URL', '{project}', 'spt_url', 'pyasm.search.SObject', 'Custom URL', 'public'); 


INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/trigger', 'config/trigger', 'config', 'Triggers', '{project}', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/process', 'config/process', 'config', 'Processes', '{project}', 'spt_process', 'pyasm.search.SObject', 'Processes', 'public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/work_hour', 'sthpw/work_hour', 'sthpw', 'Work Hours', 'sthpw', 'work_hour', 'pyasm.biz.WorkHour', 'Work Hours', 'public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sobject_list', 'sthpw/sobject_list', 'sthpw', 'SObject List', 'sthpw', 'sobject_list', 'pyasm.search.SObject', 'SObjectList', 'public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES('sthpw/milestone','sthpw/milestone','sthpw','Project Milestones','sthpw','milestone','pyasm.biz.Milestone','Project Milestones','public');

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/plugin', 'config/plugin', 'config', 'Plugin', '{project}', 'spt_plugin', 'pyasm.search.SObject', 'Plugin', 'public'); 

-- This is still needed for VFX template.

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('prod/session_contents', 'prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public');

-- CREATE extra indices

CREATE INDEX "note_search_type_search_id_idx" on note (search_type, search_id);
CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id);
CREATE INDEX "sobject_list_search_type_search_id_idx" on sobject_list (search_type, search_id);
CREATE INDEX "status_log_search_type_search_id_idx" on status_log (search_type, search_id);
CREATE INDEX "task_search_type_search_id_idx" on task (search_type, search_id);
CREATE INDEX "connection_dst_search_type_dst_search_id_context_idx" on connection (dst_search_type, dst_search_id, context);
CREATE INDEX "connection_src_search_type_src_search_id_idx" on connection (src_search_type, src_search_id);




