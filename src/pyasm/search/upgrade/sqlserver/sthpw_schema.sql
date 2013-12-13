SET QUOTED_IDENTIFIER ON;
--
--

CREATE TABLE db_resource (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    host nvarchar(max),
    port integer,
    vendor nvarchar(256),
    login nvarchar(256),
    password nvarchar(max),
    CONSTRAINT "db_resource_code_idx" UNIQUE (code)
);

CREATE TABLE access_log (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    url nvarchar(256),
    data nvarchar(256),
    "start_time" datetime2(6),
    "end_time" datetime2(6),
    duration double precision,
    CONSTRAINT "access_log_code_idx" UNIQUE (code)
);


CREATE TABLE command_log (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    class_name nvarchar(100) NOT NULL,
    paramaters nvarchar(256),
    login nvarchar(100) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    CONSTRAINT "command_log_code_idx" UNIQUE (code)
);


CREATE TABLE connection (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    context nvarchar(60),
    project_code nvarchar(30),
    src_search_type nvarchar(200),
    src_search_id integer,
    dst_search_type nvarchar(200),
    dst_search_id integer,
    login nvarchar(30),
    "timestamp" datetime2(6) DEFAULT (getdate())
);


CREATE TABLE file_access (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    file_code integer NOT NULL,
    login nvarchar(100),
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL
);



CREATE TABLE queue (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    queue nvarchar(30) NOT NULL,
    priority nvarchar(10) NOT NULL,
    description nvarchar(256),
    state nvarchar(30) NOT NULL DEFAULT 'pending',
    login nvarchar(30) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    command nvarchar(200) NOT NULL,
    serialized nvarchar(256) NOT NULL,
    s_status nvarchar(30),
    project_code nvarchar(100),
    search_id integer,
    search_type nvarchar(100),
    dispatcher_id integer,
    policy_code nvarchar(30),
    host nvarchar(256)
);


CREATE TABLE repo (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256) NOT NULL,
    description nvarchar(256) NOT NULL,
    handler nvarchar(100) NOT NULL,
    web_dir nvarchar(256) NOT NULL,
    lib_dir nvarchar(256) NOT NULL
);


CREATE TABLE snapshot_type (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    pipeline_code nvarchar(256),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    login nvarchar(256),
    s_status nvarchar(256),
    relpath nvarchar(256),
    project_code nvarchar(256),
    subcontext nvarchar(256),
    snapshot_flavor nvarchar(256),
    relfile nvarchar(256),
    CONSTRAINT "snapshot_type_code_unique" UNIQUE (code)
);


CREATE TABLE special_day (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    week integer,
    mon float, 
    tue float, 
    wed float, 
    thu float, 
    fri float, 
    sat float, 
    sun float, 
    year integer, 
    login nvarchar(256),
    description nvarchar(256),
    "type" nvarchar(256),
    project_code nvarchar(256)
);


CREATE TABLE custom_property (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(256),
    name nvarchar(256),
    description nvarchar(256),
    login nvarchar(256)
);


CREATE TABLE pref_list (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    "key" nvarchar(256),
    description nvarchar(256),
    options nvarchar(256),
    "type" nvarchar(256),
    category nvarchar(256),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    title nvarchar(256),
    CONSTRAINT "pref_list_key_idx" UNIQUE ("key")
);



CREATE TABLE retire_log (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(100),
    search_id nvarchar(100),
    login nvarchar(100) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()),
    CONSTRAINT "retire_log_code_idx" UNIQUE (code)
);


CREATE TABLE translation (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    language nvarchar(256),
    msgid nvarchar(256),
    msgstr nvarchar(256),
    line nvarchar(256),
    login nvarchar(256),
    "timestamp" datetime2(6) DEFAULT (getdate())
);


CREATE TABLE project_type (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(30),
    dir_naming_cls nvarchar(200),
    file_naming_cls nvarchar(200),
    code_naming_cls nvarchar(200),
    node_naming_cls nvarchar(200),
    sobject_mapping_cls nvarchar(200),
    s_status nvarchar(32),
    "type" nvarchar(100) NOT NULL,
    repo_handler_cls nvarchar(200),
    CONSTRAINT "project_type_code_idx" UNIQUE (code)
);



CREATE TABLE login_group (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    login_group nvarchar(100) NOT NULL,
    sub_groups nvarchar(max),
    access_rules nvarchar(max),
    redirect_url nvarchar(max),
    namespace nvarchar(255),
    description nvarchar(max),
    project_code nvarchar(max),
    s_status nvarchar(256),
    start_link nvarchar(max),
    access_level nvarchar(32),
    CONSTRAINT "login_group_code_idx" UNIQUE (code)
);



CREATE TABLE login_in_group (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    "login" nvarchar(100) NOT NULL,
    login_group nvarchar(100) NOT NULL
);



CREATE TABLE ticket (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    ticket nvarchar(100) NOT NULL,
    "login" nvarchar(100),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    expiry datetime2(6),
    category nvarchar(256),
    CONSTRAINT "ticket_code_idx" UNIQUE (code),
    CONSTRAINT "ticket_ticket_idx" UNIQUE (ticket)
);




CREATE TABLE pipeline (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    pipeline nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    search_type nvarchar(100),
    project_code nvarchar(30),
    description nvarchar(max),
    color nvarchar(256),
    s_status nvarchar(30),
    autocreate_tasks BIT,
    CONSTRAINT "pipeline_code_idx" UNIQUE (code)
);



-- FIXME: Is this needed anymore?
-- FIXME: notification_id will be deprecated in 4.0
CREATE TABLE group_notification (
    id integer IDENTITY PRIMARY KEY,
    login_group nvarchar(100) NOT NULL,
    notification_id integer NOT NULL
);
CREATE TABLE notification_login (
    id integer IDENTITY PRIMARY KEY,
    notification_log_id integer,
    "login" nvarchar(256),
    "type" nvarchar(256),
    project_code nvarchar(256),
    "timestamp" datetime2(6) DEFAULT (getdate())
);



CREATE TABLE notification_log (
    id integer IDENTITY PRIMARY KEY,
    project_code nvarchar(256),
    "login" nvarchar(256),
    command_cls nvarchar(256),
    subject nvarchar(max),
    message nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate())
);


CREATE TABLE snapshot (
    id integer IDENTITY PRIMARY KEY,
    search_type nvarchar(100) NOT NULL,
    search_id integer NOT NULL,
    column_name nvarchar(100) NOT NULL,
    snapshot nvarchar(max) NOT NULL,
    description nvarchar(max),
    process nvarchar(256),
    "login" nvarchar(100) NOT NULL,
    "lock_login" nvarchar(100),
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    lock_date datetime2(6),
    context nvarchar(256),
    version integer,
    s_status nvarchar(30),
    snapshot_type nvarchar(30),
    code nvarchar(30),
    repo nvarchar(30),
    is_current BIT,
    label nvarchar(100),
    revision smallint,
    level_type nvarchar(256),
    level_id integer,
    metadata nvarchar(max),
    is_latest BIT,
    status nvarchar(256),
    project_code nvarchar(256),
    search_code nvarchar(256),
    is_synced BIT,
    CONSTRAINT "snapshot_code_idx" UNIQUE (code)
);

CREATE TABLE "file" (
    id integer IDENTITY PRIMARY KEY,
    file_name nvarchar(512),
    search_type nvarchar(100) NOT NULL,
    search_id integer NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    st_size bigint,
    file_range nvarchar(max),
    code nvarchar(30),
    snapshot_code nvarchar(30),
    project_code nvarchar(100),
    md5 nvarchar(32),
    checkin_dir nvarchar(max),
    source_path nvarchar(max),
    relative_dir nvarchar(max),
    "type" nvarchar(256),
    base_type nvarchar(256),
    metadata nvarchar(max),
    metadata_search nvarchar(max), 
    repo_type nvarchar(256), 
    "base_dir_alias" nvarchar(256),
    
    CONSTRAINT "file_code_idx" UNIQUE (code)
);



-- NOTE: is this really needed anymore?  Check-in is dependent on it!
CREATE TABLE remote_repo (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(30),
    ip_address nvarchar(30),
    ip_mask nvarchar(30),
    repo_base_dir nvarchar(200),
    sandbox_base_dir nvarchar(200),
    "login" nvarchar(100),
    CONSTRAINT "remote_repo_code_idx" UNIQUE (code)
);




CREATE TABLE milestone (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    project_code nvarchar(256),
    description nvarchar(max),
    due_date datetime2(6),
    CONSTRAINT "milestone_code_idx" UNIQUE (code)
);




-- NOTE: file name is deleted
CREATE TABLE task (
    id integer IDENTITY PRIMARY KEY,
    -- file_name nvarchar(512) NOT NULL,
    assigned nvarchar(100),
    description nvarchar(max),
    status nvarchar(256),
    discussion nvarchar(max),
    bid_start_date datetime2(6),
    bid_end_date datetime2(6),
    bid_duration double precision,
    actual_start_date datetime2(6),
    actual_end_date datetime2(6),
    search_type nvarchar(100),
    search_id integer,
    "timestamp" datetime2(6) DEFAULT (getdate()),
    s_status nvarchar(30),
    priority smallint,
    process nvarchar(256),
    context nvarchar(256),
    milestone_code nvarchar(200),
    pipeline_code nvarchar(256),
    parent_id integer,
    sort_order smallint,
    depend_id integer,
    project_code nvarchar(100),
    supervisor nvarchar(100),
    code nvarchar(256),
    login nvarchar(256),
    completion float,
    CONSTRAINT "task_code_idx" UNIQUE (code)
);


CREATE TABLE note (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    project_code nvarchar(30),
    search_type nvarchar(200),
    search_id integer,
    "login" nvarchar(30),
    context nvarchar(60),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    note nvarchar(max),
    title nvarchar(1024),
    parent_id bigint,
    status nvarchar(256),
    label nvarchar(256),
    process nvarchar(60),
    "sort_order" integer,
    "access" nvarchar(256),
    CONSTRAINT "note_code_idx" UNIQUE (code)
);




CREATE TABLE pref_setting (
    id integer IDENTITY PRIMARY KEY,
    project_code nvarchar(256),
    "login" nvarchar(256),
    "key" nvarchar(256),
    value nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate())
);


CREATE TABLE wdg_settings (
    id integer IDENTITY PRIMARY KEY,
    "key" nvarchar(255) NOT NULL,
    "login" nvarchar(100) NOT NULL,
    data nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    project_code nvarchar(30)
);



CREATE TABLE clipboard (
    id integer IDENTITY PRIMARY KEY,
    project_code nvarchar(256),
    "login" nvarchar(256),
    search_type nvarchar(256),
    search_id integer,
    "timestamp" datetime2(6) DEFAULT (getdate()),
    category nvarchar(256)
);






CREATE TABLE exception_log (
    id integer IDENTITY PRIMARY KEY,
    "class" nvarchar(100),
    message nvarchar(max),
    stack_trace nvarchar(max),
    "login" nvarchar(100) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL
);




CREATE TABLE transaction_log (
    id integer IDENTITY PRIMARY KEY,
    "code" nvarchar(256),
    "transaction" nvarchar(max),
    "login" nvarchar(100) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    description nvarchar(max),
    command nvarchar(100),
    title nvarchar(max),
    "type" nvarchar(30),
    namespace nvarchar(100),
    CONSTRAINT "transaction_log_code_idx" UNIQUE (code)
);

CREATE INDEX "transaction_log_timestamp_idx" ON transaction_log ("timestamp");
CREATE INDEX "transaction_log_idx" ON transaction_log (login, namespace, "type");





-- FIXME: is this really needed???
CREATE TABLE transaction_state (
    id integer IDENTITY PRIMARY KEY,
    ticket nvarchar(100),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    data nvarchar(max),
    CONSTRAINT "transaction_state_ticket_idx" UNIQUE (ticket)
);




CREATE TABLE sobject_log (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(100) NOT NULL,
    search_id integer NOT NULL,
    data nvarchar(max),
    "login" nvarchar(100) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    transaction_log_id integer
);


CREATE TABLE status_log (
    id integer IDENTITY PRIMARY KEY,
    search_type nvarchar(256) NOT NULL,
    search_id integer NOT NULL,
    status nvarchar(256),
    "login" nvarchar(256) NOT NULL,
    "timestamp" datetime2(6) DEFAULT (getdate()) NOT NULL,
    to_status nvarchar(256),
    from_status nvarchar(256),
    project_code nvarchar(256)
);

CREATE TABLE debug_log (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    category nvarchar(256),
    "level" nvarchar(256),
    message nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    "login" nvarchar(256),
    s_status nvarchar(30)
);



CREATE TABLE work_hour (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    project_code nvarchar(256),
    description nvarchar(max),
    category nvarchar(256),
    process nvarchar(256),
    "login" nvarchar(256),
    "day" datetime2(6),
    start_time datetime2(6),
    end_time datetime2(6),
    straight_time double precision,
    over_time double precision,
    search_type nvarchar(256),
    search_id integer,
    status nvarchar(256),
    task_code nvarchar(256),
    CONSTRAINT "work_hour_code_idx" UNIQUE (code)
);






-- in upgrade
CREATE TABLE cache (
    id integer IDENTITY PRIMARY KEY,
    "key" nvarchar(256),
    mtime datetime2(6)
);


CREATE TABLE sobject_list (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(256),
    search_id integer,
    keywords nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    project_code nvarchar(256),
    CONSTRAINT "sobject_list_code_idx" UNIQUE (code)
);


-- sync
CREATE TABLE change_timestamp (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    search_type nvarchar(256),
    search_code nvarchar(256),
    changed_on nvarchar(max),
    changed_by nvarchar(max),
    project_code nvarchar(256),
    transaction_code nvarchar(256)
);





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

INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/pipeline', 'config/pipeline', 'config', 'Pipelines', '{project}', 'spt_pipeline', 'pyasm.search.SObject', 'Pipelines', 'public');


-- This is still needed for VFX template.

INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('prod/session_contents', 'prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public');


-- pref_list

INSERT INTO pref_list ("key", description, options, "type", category, title) VALUES ('skin', 'These skins determine the look and feel of  TACTIC.', 'classic|dark|light|lightdark', 'sequence', 'general', 'Tactic Skins');

INSERT INTO pref_list ("key", description, options, "type", category, title) VALUES ('thumb_multiplier', 'Determines the size multiplier of all thumbnail images', '1|2|0.5', 'sequence', 'general', 'Thumb Size');

INSERT INTO pref_list ("key", description, options, "type", category, title) VALUES ('js_logging_level','Determines logging level used by Web Client Output Console Pop-up','CRITICAL|ERROR|WARNING|INFO|DEBUG','sequence','general','Web Client Logging Level');
INSERT INTO pref_list ("key", description, options, "type", category, title) VALUES ('quick_text','Quick nvarchar(max) for Note Sheet','','string','general','Quick Text');

-- sample pipelines

INSERT INTO pipeline (code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES ('model', '<?xml version="1.0" encoding="UTF-8"?>  
<pipeline="serial">  
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
INSERT INTO pipeline (code, pipeline, "timestamp", search_type, project_code, description, s_status) VALUES ('shot', '<?xml version="1.0" encoding="UTF-8"?> 
<pipeline="parallel"> 
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


-- CREATE extra indices

CREATE INDEX "note_search_type_search_id_idx" on note (search_type, search_id);
CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id);
CREATE INDEX "sobject_list_search_type_search_id_idx" on sobject_list (search_type, search_id);
CREATE INDEX "status_log_search_type_search_id_idx" on status_log (search_type, search_id);
CREATE INDEX "task_search_type_search_id_idx" on task (search_type, search_id);
CREATE INDEX "connection_dst_search_type_dst_search_id_context_idx" on connection (dst_search_type, dst_search_id, context);
CREATE INDEX "connection_src_search_type_src_search_id_idx" on connection (src_search_type, src_search_id);




