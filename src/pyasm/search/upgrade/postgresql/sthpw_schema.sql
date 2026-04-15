--
--

CREATE TABLE "db_resource" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "host" text,
    "port" integer,
    "vendor" character varying(256),
    "login" character varying(256),
    "password" text,
    CONSTRAINT "db_resource_code_idx" UNIQUE ("code")
);


CREATE TABLE "access_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "url" character varying(256),
    "data" character varying(256),
    "start_time" timestamp,
    "end_time" timestamp,
    "duration" float,
    CONSTRAINT "access_log_code_idx" UNIQUE ("code")
);


CREATE TABLE "command_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "class_name" character varying(100) NOT NULL,
    "paramaters" character varying(256),
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT "command_log_code_idx" UNIQUE ("code")
);


CREATE TABLE "connection" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "context" character varying(60),
    "project_code" character varying(30),
    "src_search_type" character varying(200),
    "src_search_id" integer,
    "dst_search_type" character varying(200),
    "dst_search_id" integer,
    "login" character varying(30),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "file_access" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "file_code" integer NOT NULL,
    "login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "queue" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "queue" character varying(30) NOT NULL,
    "priority" character varying(10) NOT NULL,
    "description" character varying(256),
    "state" character varying(30) DEFAULT 'pending' NOT NULL,
    "login" character varying(30) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "command" character varying(200) NOT NULL,
    "serialized" character varying(256),
    "s_status" character varying(30),
    "project_code" character varying(100),
    "search_id" integer,
    "search_type" character varying(100),
    "dispatcher_id" integer,
    "policy_code" character varying(30),
    "host" character varying(256)
);


CREATE TABLE "repo" (
    "id" serial PRIMARY KEY,
    "code" character varying(256) NOT NULL,
    "description" character varying(256) NOT NULL,
    "handler" character varying(100) NOT NULL,
    "web_dir" character varying(256) NOT NULL,
    "lib_dir" character varying(256) NOT NULL
);


CREATE TABLE "snapshot_type" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "pipeline_code" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "login" character varying(256),
    "s_status" character varying(256),
    "relpath" character varying(256),
    "project_code" character varying(256),
    "subcontext" character varying(256),
    "snapshot_flavor" character varying(256),
    "relfile" character varying(256),
    CONSTRAINT "snapshot_type_code_unique" UNIQUE ("code")
);


CREATE TABLE "special_day" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "week" integer,
    "mon" float, 
    "tue" float, 
    "wed" float, 
    "thu" float, 
    "fri" float, 
    "sat" float, 
    "sun" float, 
    "year" integer, 
    "login" character varying(256),
    "description" character varying(256),
    "type" character varying(256),
    "project_code" character varying(256)
);


CREATE TABLE "custom_property" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "search_type" character varying(256),
    "name" character varying(256),
    "description" character varying(256),
    "login" character varying(256)
);


CREATE TABLE "pref_list" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "key" character varying(256),
    "description" character varying(256),
    "options" character varying(256),
    "type" character varying(256),
    "category" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "title" character varying(256),
    CONSTRAINT "pref_list_key_idx" UNIQUE ("key")
);


CREATE TABLE "retire_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "search_type" character varying(100),
    "search_id" character varying(100),
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT "retire_log_code_idx" UNIQUE ("code")
);


CREATE TABLE "translation" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "language" character varying(256),
    "msgid" character varying(256),
    "msgstr" character varying(256),
    "line" character varying(256),
    "login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "project_type" (
    "id" serial PRIMARY KEY,
    "code" character varying(30),
    "dir_naming_cls" character varying(200),
    "file_naming_cls" character varying(200),
    "code_naming_cls" character varying(200),
    "node_naming_cls" character varying(200),
    "sobject_mapping_cls" character varying(200),
    "s_status" character varying(32),
    "type" character varying(100) NOT NULL,
    "repo_handler_cls" character varying(200),
    CONSTRAINT "project_type_code_idx" UNIQUE ("code")
);


CREATE TABLE "login_group" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "login_group" character varying(100) NOT NULL,
    "name" text,
    "sub_groups" text,
    "access_rules" text,
    "redirect_url" text,
    "namespace" character varying(255),
    "description" text,
    "project_code" text,
    "s_status" character varying(256),
    "start_link" text,
    "access_level" character varying(32),
    "is_default" boolean,
    "data" jsonb,
    CONSTRAINT "login_group_code_idx" UNIQUE ("code")
);


CREATE TABLE "login_in_group" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "login" character varying(100) NOT NULL,
    "login_group" character varying(100) NOT NULL
);


CREATE TABLE "ticket" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "ticket" character varying(100) NOT NULL,
    "login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "expiry" timestamp,
    "category" character varying(256),
    CONSTRAINT "ticket_code_idx" UNIQUE ("code"),
    CONSTRAINT "ticket_ticket_idx" UNIQUE ("ticket")
);


CREATE TABLE "pipeline" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "pipeline" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "search_type" character varying(100),
    "project_code" character varying(30),
    "description" text,
    "color" character varying(256),
    "s_status" character varying(30),
    "autocreate_tasks" boolean,
    "use_workflow" boolean default true,
    CONSTRAINT "pipeline_code_idx" UNIQUE ("code")
);


CREATE TABLE "group_notification" (
    "id" serial PRIMARY KEY,
    "login_group" character varying(100) NOT NULL,
    "notification_id" integer NOT NULL
);


CREATE TABLE "notification_login" (
    "id" serial PRIMARY KEY,
    "notification_log_id" integer,
    "login" character varying(256),
    "type" character varying(256),
    "project_code" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "notification_log" (
    "id" serial PRIMARY KEY,
    "project_code" character varying(256),
    "login" character varying(256),
    "command_cls" character varying(256),
    "subject" text,
    "message" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "snapshot" (
    "id" serial PRIMARY KEY,
    "search_type" character varying(100) NOT NULL,
    "search_id" integer NOT NULL,
    "column_name" character varying(100) NOT NULL,
    "snapshot" text NOT NULL,
    "description" text,
    "process" character varying(256),
    "login" character varying(100) NOT NULL,
    "lock_login" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "lock_date" timestamp,
    "context" character varying(256),
    "version" integer,
    "s_status" character varying(30),
    "snapshot_type" character varying(30),
    "code" character varying(30),
    "repo" character varying(30),
    "is_current" boolean,
    "label" character varying(100),
    "revision" integer,
    "level_type" character varying(256),
    "level_id" integer,
    "metadata" text,
    "is_latest" boolean,
    "status" character varying(256),
    "project_code" character varying(256),
    "search_code" character varying(256),
    "is_synced" boolean,
    CONSTRAINT "snapshot_code_idx" UNIQUE ("code")
);


CREATE TABLE "file" (
    "id" serial PRIMARY KEY,
    "file_name" character varying(512),
    "search_type" character varying(100) NOT NULL,
    "search_id" integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "st_size" integer,
    "file_range" text,
    "code" character varying(30),
    "snapshot_code" character varying(30),
    "project_code" character varying(100),
    "md5" character varying(32),
    "checkin_dir" text,
    "source_path" text,
    "relative_dir" text,
    "type" character varying(256),
    "base_type" character varying(256),
    "metadata" text,
    "metadata_search" text, 
    "repo_type" character varying(256), 
    "base_dir_alias" character varying(256),
    CONSTRAINT "file_code_idx" UNIQUE ("code")
);


CREATE TABLE "remote_repo" (
    "id" serial PRIMARY KEY,
    "code" character varying(30),
    "ip_address" character varying(30),
    "ip_mask" character varying(30),
    "repo_base_dir" character varying(200),
    "sandbox_base_dir" character varying(200),
    "login" character varying(100),
    CONSTRAINT "remote_repo_code_idx" UNIQUE ("code")
);


CREATE TABLE "milestone" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "project_code" character varying(256),
    "description" text,
    "due_date" timestamp,
    CONSTRAINT "milestone_code_idx" UNIQUE ("code")
);


CREATE TABLE "task" (
    "id" serial PRIMARY KEY,
    "assigned" character varying(100),
    "description" text,
    "status" character varying(32),
    "discussion" text,
    "bid_start_date" timestamp,
    "bid_end_date" timestamp,
    "bid_duration" float,
    "actual_start_date" timestamp,
    "actual_end_date" timestamp,
    "search_type" character varying(100),
    "search_id" integer,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "s_status" character varying(30),
    "priority" integer,
    "process" character varying(256),
    "context" character varying(256),
    "milestone_code" character varying(200),
    "pipeline_code" character varying(256),
    "parent_id" integer,
    "sort_order" integer,
    "depend_id" integer,
    "project_code" character varying(100),
    "supervisor" character varying(100),
    "code" character varying(256),
    "login" character varying(256),
    "completion" float,
    CONSTRAINT "task_code_idx" UNIQUE ("code")
);


CREATE TABLE "note" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "project_code" character varying(30),
    "search_type" character varying(200),
    "search_id" integer,
    "login" character varying(30),
    "context" character varying(60),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "note" text,
    "title" character varying(1024),
    "parent_id" integer,
    "status" character varying(256),
    "label" character varying(256),
    "process" character varying(60),
    "sort_order" integer,
    "access" character varying(256),
    CONSTRAINT "note_code_idx" UNIQUE ("code")
);


CREATE TABLE "pref_setting" (
    "id" serial PRIMARY KEY,
    "project_code" character varying(256),
    "login" character varying(256),
    "key" character varying(256),
    "value" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "wdg_settings" (
    "id" serial PRIMARY KEY,
    "key" character varying(255) NOT NULL,
    "login" character varying(100) NOT NULL,
    "data" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "project_code" character varying(30)
);


CREATE TABLE "clipboard" (
    "id" serial PRIMARY KEY,
    "project_code" character varying(256),
    "login" character varying(256),
    "search_type" character varying(256),
    "search_id" integer,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "category" character varying(256)
);


CREATE TABLE "exception_log" (
    "id" serial PRIMARY KEY,
    "class" character varying(100),
    "message" text,
    "stack_trace" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "transaction_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "transaction" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "description" text,
    "command" character varying(100),
    "title" text,
    "type" character varying(30),
    "namespace" character varying(100),
    CONSTRAINT "transaction_log_code_idx" UNIQUE ("code")
);


CREATE INDEX "transaction_log_timestamp_idx" ON "transaction_log" ("timestamp");
CREATE INDEX "transaction_log_idx" ON "transaction_log" ("login", "namespace", "type");

CREATE TABLE "transaction_state" (
    "id" serial PRIMARY KEY,
    "ticket" character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "data" text,
    CONSTRAINT "transaction_state_ticket_idx" UNIQUE ("ticket")
);


CREATE TABLE "sobject_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "search_type" character varying(100) NOT NULL,
    "search_id" integer NOT NULL,
    "data" text,
    "login" character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "transaction_log_id" integer
);


CREATE TABLE "status_log" (
    "id" serial PRIMARY KEY,
    "search_type" character varying(256) NOT NULL,
    "search_id" integer NOT NULL,
    "status" text,
    "login" character varying(256) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "to_status" character varying(256),
    "from_status" character varying(256),
    "project_code" character varying(256)
);


CREATE TABLE "debug_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "category" character varying(256),
    "level" character varying(256),
    "message" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "login" character varying(256),
    "s_status" character varying(30)
);


CREATE TABLE "work_hour" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "project_code" character varying(256),
    "description" text,
    "category" character varying(256),
    "process" character varying(256),
    "login" character varying(256),
    "day" timestamp,
    "start_time" timestamp,
    "end_time" timestamp,
    "straight_time" float,
    "over_time" float,
    "search_type" character varying(256),
    "search_id" integer,
    "status" character varying(256),
    "task_code" character varying(256),
    CONSTRAINT "work_hour_code_idx" UNIQUE ("code")
);


CREATE TABLE "cache" (
    "id" serial PRIMARY KEY,
    "key" character varying(256),
    "mtime" timestamp
);


CREATE TABLE "sobject_list" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "search_type" character varying(256),
    "search_id" integer,
    "keywords" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "project_code" character varying(256),
    CONSTRAINT "sobject_list_code_idx" UNIQUE ("code")
);


CREATE TABLE "change_timestamp" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "search_type" character varying(256),
    "search_code" character varying(256),
    "changed_on" text,
    "changed_by" text,
    "project_code" character varying(256),
    "transaction_code" character varying(256)
);


CREATE TABLE "interaction" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "project_code" character varying(256),
    "login" character varying(256),
    "key" character varying(1024),
    "data" text,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE INDEX "interaction_key_idx" on "interaction" ("key");

-- CREATE extra indices
CREATE INDEX "note_search_type_search_id_idx" on "note" ("search_type", "search_id");
CREATE INDEX "snapshot_stype_sid_idx" on "snapshot" ("search_type", "search_id");
CREATE INDEX "sobject_list_stype_sid_idx" on "sobject_list" ("search_type", "search_id");
CREATE INDEX "status_log_stype_sid_idx" on "status_log" ("search_type", "search_id");
CREATE INDEX "task_search_type_search_id_idx" on "task" ("search_type", "search_id");
CREATE INDEX "con_d_stype_d_sid_con_idx" on "connection" ("dst_search_type", "dst_search_id", "context");
CREATE INDEX "con_s_stype_s_sid_idx" on "connection" ("src_search_type", "src_search_id");


INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/db_resource', 'sthpw/db_resource', 'sthpw', 'Database Resource', 'sthpw', 'db_resource', 'pyasm.search.SObject', 'Database Resource', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/custom_property', 'config/custom_property', 'sthpw', 'Custom Property', '{project}', 'custom_property', 'pyasm.biz.CustomProperty', 'Custom Property', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/annotation', 'sthpw/annotation', 'sthpw', 'Image Annotations', 'sthpw', 'annotation', 'pyasm.search.search.SObject', 'Image Annotations', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/retire_log', 'sthpw/retire_log', 'sthpw', 'Retire SObject log', 'sthpw', 'retire_log', 'pyasm.search.RetireLog', 'Retire SObject log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/login_in_group', 'sthpw/login_in_group', 'sthpw', 'Users in groups', 'sthpw', 'login_in_group', 'pyasm.security.LoginInGroup', 'Users in groups', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/exception_log', 'sthpw/exception_log', 'sthpw', 'Exception Log', 'sthpw', 'exception_log', 'pyasm.search.SObject', 'Exception Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/file_access', 'sthpw/file_access', 'sthpw', 'File Access Log', 'sthpw', 'file_access', 'pyasm.biz.FileAccess', 'File Access Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/repo', 'sthpw/repo', 'sthpw', 'Repository List', 'sthpw', 'repo', 'pyasm.search.SObject', 'Repository List', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/queue', 'sthpw/queue', 'sthpw', 'Tactic Dispatcher', 'sthpw', 'queue', 'pyasm.search.SObject', 'Tactic Dispatcher', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/task', 'sthpw/task', 'sthpw', 'User Tasks', 'sthpw', 'task', 'pyasm.biz.Task', 'User Tasks', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sobject_config', 'sthpw/sobject_config', 'sthpw', 'SObject Config Data', 'sthpw', 'sobject_config', 'pyasm.search.SObjectDbConfig', 'SObject Config Data', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/transaction_state', 'sthpw/transaction_state', 'sthpw', 'XMLRPC State', 'sthpw', 'transaction_state', 'pyasm.search.TransactionState', 'transaction_state', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/command', 'sthpw/command', 'sthpw', 'Commands in Tactic', 'sthpw', 'command', 'pyasm.biz.CommandSObj', 'Commands in Tactic', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/command_log', 'sthpw/command_log', 'sthpw', 'Historical log of all of the commands executed', 'sthpw', 'command_log', 'pyasm.command.CommandLog', 'Command Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/file', 'sthpw/file', 'sthpw', 'A record of all files that are tracked', 'sthpw', 'file', 'pyasm.biz.file.File', 'File', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/login_group', 'sthpw/login_group', 'sthpw', 'List of groups that user belong to', 'sthpw', 'login_group', 'pyasm.security.LoginGroup', 'Groups', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/note', 'sthpw/note', 'sthpw', 'Notes', 'sthpw', 'note', 'pyasm.biz.Note', 'Notes', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/pipeline', 'sthpw/pipeline', 'sthpw', 'List of piplines available for sobjects', 'sthpw', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/status_log', 'sthpw/status_log', 'sthpw', 'Log of status changes', 'sthpw', 'status_log', 'pyasm.search.SObject', 'Status Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/group_notification', 'sthpw/group_notification', 'sthpw', 'Associate one of more kinds of notification with groups', 'sthpw', 'group_notification', 'pyasm.biz.GroupNotification', 'Group Notification', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/snapshot', 'sthpw/snapshot', 'sthpw', 'All versions of snapshots of assets', 'sthpw', 'snapshot', 'pyasm.biz.Snapshot', 'Snapshot', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/ticket', 'sthpw/ticket', 'sthpw', 'Valid login tickets to enter the system', 'sthpw', 'ticket', 'pyasm.security.Ticket', 'Ticket', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/wdg_settings', 'sthpw/wdg_settings', 'sthpw', 'Persistent store for widgets to remember user settings', 'sthpw', 'wdg_settings', 'pyasm.web.WidgetSettings', 'Widget Settings', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/transaction_log', 'sthpw/transaction_log', 'sthpw', NULL, 'sthpw', 'transaction_log', 'pyasm.search.TransactionLog', 'Transaction Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sobject_log', 'sthpw/sobject_log', 'sthpw', 'Log of actions on an sobject', 'sthpw', 'sobject_log', 'pyasm.search.SObject', 'SObject Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/project_type', 'sthpw/project_type', 'sthpw', 'Project Type', 'sthpw', 'project_type', 'pyasm.biz.ProjectType', 'Project Type', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/pref_setting', 'sthpw/pref_setting', 'sthpw', 'Preference Setting', 'sthpw', '{public}.pref_setting', 'pyasm.biz.PrefSetting', 'Pref Setting', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/clipboard', 'sthpw/clipboard', 'sthpw', 'Clipboard', 'sthpw', '{public}.clipboard', 'pyasm.biz.Clipboard', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/pref_list', 'sthpw/pref_list', 'sthpw', 'Preferences List', 'sthpw', '{public}.pref_list', 'pyasm.biz.PrefList', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/translation', 'sthpw/translation', 'sthpw', 'Locale Translations', 'sthpw', '{public}.translation', 'pyasm.search.SObject', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/notification_log', 'sthpw/notification_log', 'sthpw', 'Notification Log', 'sthpw', '{public}.notification_log', 'pyasm.search.SObject', 'Notification Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/notification_login', 'sthpw/notification_login', 'sthpw', 'Notification Login', 'sthpw', '{public}.notification_login', 'pyasm.search.SObject', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/connection', 'sthpw/connection', 'sthpw', 'Connections', 'sthpw', 'connection', 'pyasm.biz.SObjectConnection', 'Connections', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/remote_repo', 'sthpw/remote_repo', 'sthpw', 'Remote Repositories', 'sthpw', 'remote_repo', 'pyasm.biz.RemoteRepo', 'Remote Repositories', NULL);

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/widget_extend', 'sthpw/widget_extend', 'sthpw', 'Extend Widget', 'sthpw', 'widget_extend', 'pyasm.search.SObject', 'widget_extend', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/snapshot_type', 'sthpw/snapshot_type', 'sthpw', 'Snapshot Type', 'sthpw', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/widget_config', 'sthpw/widget_config', 'sthpw', 'Widget Config Data', 'sthpw', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config Data', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/debug_log', 'sthpw/debug_log', 'sthpw', 'Debug Log', 'sthpw', 'debug_log', 'pyasm.biz.DebugLog', 'Debug Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('unittest/person', 'unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('unittest/city', 'unittest/city', 'unittest', 'Unittest City', 'unittest', 'city', 'pyasm.search.SObject', 'Unittest City', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('unittest/country', 'unittest/country', 'unittest', 'Unittest Country', 'unittest', 'country', 'pyasm.search.SObject', 'Unittest Country', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/widget_config', 'config/widget_config', 'config', 'Widget Config', '{project}', 'spt_widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/custom_script', 'sthpw/custom_script', 'sthpw', 'Central Custom Script', 'sthpw', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/custom_script', 'config/custom_script', 'config', 'Custom Script', '{project}', 'spt_custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/naming', 'config/naming', 'config', 'Naming', '{project}', '{public}.spt_naming', 'pyasm.biz.Naming', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/cache', 'sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/prod_setting', 'config/prod_setting', 'config', 'Production Settings', '{project}', 'spt_prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/client_trigger', 'config/client_trigger', 'config', 'Client Trigger', '{project}', 'spt_client_trigger', 'pyasm.search.SObject', 'Client Trigger', 'public'); 

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/url', 'config/url', 'config', 'Custom URL', '{project}', 'spt_url', 'pyasm.search.SObject', 'Custom URL', 'public'); 

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/trigger', 'config/trigger', 'config', 'Triggers', '{project}', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/process', 'config/process', 'config', 'Processes', '{project}', 'spt_process', 'pyasm.search.SObject', 'Processes', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/work_hour', 'sthpw/work_hour', 'sthpw', 'Work Hours', 'sthpw', 'work_hour', 'pyasm.biz.WorkHour', 'Work Hours', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sobject_list', 'sthpw/sobject_list', 'sthpw', 'SObject List', 'sthpw', 'sobject_list', 'pyasm.search.SObject', 'SObjectList', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/milestone','sthpw/milestone','sthpw','Project Milestones','sthpw','milestone','pyasm.biz.Milestone','Project Milestones','public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/department','sthpw/department','sthpw','Department','sthpw','department','pyasm.search.SObject','Department','public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/interaction', 'sthpw/interaction', 'sthpw', 'User Interaction', 'sthpw', 'interaction', 'pyasm.search.SObject', 'User Interaction', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/plugin', 'config/plugin', 'config', 'Plugin', '{project}', 'spt_plugin', 'pyasm.search.SObject', 'Plugin', 'public'); 

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/pipeline', 'config/pipeline', 'config', 'Pipelines', '{project}', 'spt_pipeline', 'pyasm.search.SObject', 'Pipelines', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/process_state', 'config/process_state', 'config', 'Process State', '{project}', 'spt_process_state', 'pyasm.search.SObject', 'Process State', 'public');


INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('prod/session_contents', 'prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public');

INSERT INTO "pref_list" ("key", "description", "options", "type", "category", "title") VALUES ('skin', 'These skins determine the look and feel of  TACTIC.', 'classic|dark|light|lightdark', 'sequence', 'general', 'Tactic Skins');

INSERT INTO "pref_list" ("key", "description", "options", "type", "category", "title") VALUES ('thumb_multiplier', 'Determines the size multiplier of all thumbnail images', '1|2|0.5', 'sequence', 'general', 'Thumb Size');

INSERT INTO "pref_list" ("key", "description", "options", "type", "category", "title") VALUES ('js_logging_level','Determines logging level used by Web Client Output Console Pop-up','CRITICAL|ERROR|WARNING|INFO|DEBUG','sequence','general','Web Client Logging Level');

INSERT INTO "pref_list" ("key", "description", "options", "type", "category", "title") VALUES ('quick_text','Quick text for Note Sheet','','string','general','Quick Text');



-- Total number of tables in 'sthpw' schema: 70 tables
-- From Southpaw OracleDB SQL scripts we have 57 tables
-- Below mentioned 13 tables are missing

-- 1. department
-- 2. doc
-- 3. message
-- 4. message_log
-- 5. spt_ingest_rule
-- 6. spt_ingest_session
-- 7. spt_plugin_content
-- 8. spt_translation
-- 9. subscription
-- 10. sync_job
-- 11. sync_log
-- 12. sync_server
-- 13. watch_folder

CREATE TABLE "department" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "name" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "doc" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "alias" character varying(1024),
	"rel_path" text
);


CREATE TABLE "message" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"category" character varying(256),
	"message" text,
	"status" character varying(32),
	"login" character varying(256),
	"project_code" character varying(32),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	CONSTRAINT "message_code_idx" UNIQUE ("code")
);


CREATE TABLE "message_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"message_code" character varying(256),
	"category" character varying(256),
	"message" text,
	"status" character varying(32),
	"login" character varying(256),
	"project_code" character varying(32),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


CREATE TABLE "subscription" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"category" character varying(256),
	"message_code" character varying(256),
	"login" character varying(256),
	"project_code" character varying(32),
	"status" character varying(32),
	"last_cleared" timestamp without time zone DEFAULT now() NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	CONSTRAINT "subscription_code_idx" UNIQUE ("code")
);


CREATE INDEX "subscription_message_code_idx" on "subscription" ("message_code");

CREATE TABLE "sync_job" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	"command" text,
	"data" text,
	"state" character varying(256),
	"host" character varying(256),
	"project_code" character varying(256),
	"error_log" text,
	"server_code" character varying(256),
	"transaction_code" character varying(256)
);


CREATE INDEX "sync_job_code_idx" on "sync_job" ("code");
CREATE INDEX "sync_job_state_idx" on "sync_job" ("state");

CREATE TABLE "sync_log" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"transaction_code" character varying(256),
	"status" character varying(256),
	"error" character varying(256),
	"login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	"project_code" character varying(256)
);


CREATE INDEX "sync_log_transaction_idx" on "sync_log" ("transaction_code");

CREATE TABLE "sync_server" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"host" character varying(256),
	"login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	"state" character varying(256),
	"ticket" character varying(256),
	"access_rules" text,
	"description" text,
	"sync_mode" character varying(256),
	"base_dir" text,
	"file_mode" character varying(256)
);


CREATE INDEX "sync_server_code_idx" on "sync_server" ("code");

CREATE TABLE "watch_folder" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"name" character varying(256),
	"project_code" character varying(256),
	"base_dir" text,
	"search_type" character varying(256),
	"process" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
	"script_path" character varying(1024)
);


INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/doc', 'sthpw/doc', 'sthpw', 'Documentation', 'sthpw', 'doc', 'pyasm.search.SObject', 'Documentation', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/message', 'sthpw/message', 'sthpw', 'Messages', 'sthpw', 'message', 'pyasm.search.SObject', 'Message', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/message_log', 'sthpw/message_log', 'sthpw', 'Message Log', 'sthpw', 'message_log', 'pyasm.search.SObject', 'Message Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/subscription', 'sthpw/subscription', 'sthpw', 'Subscription', 'sthpw', 'subscription', 'pyasm.search.SObject', 'Subscription', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sync_job', 'sthpw/sync_job', 'sthpw', 'Sync Job', 'sthpw', 'sync_job', 'pyasm.search.SObject', 'Sync Job', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sync_log', 'sthpw/sync_log', 'sthpw', 'List of all processed incoming sync jobs', 'sthpw', 'sync_log', 'pyasm.search.SObject', 'Sync Log', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sync_server', 'sthpw/sync_server', 'sthpw', 'Sync Server', 'sthpw', 'sync_server', 'pyasm.search.SObject', 'Sync Server', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/watch_folder', 'sthpw/watch_folder', 'sthpw', 'Watch Folder', 'sthpw', 'watch_folder', 'pyasm.search.SObject', 'Watch Folder', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/ingest_rule', 'config/ingest_rule', 'config', 'Ingest Rules', '{project}', 'spt_ingest_rule', 'pyasm.search.SObject', 'Ingest Rules', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/ingest_session', 'config/ingest_session', 'config', 'Ingest Sessions', '{project}', 'spt_ingest_session', 'pyasm.search.SObject', 'Ingest Sessions', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/plugin_content', 'config/plugin_content', 'config', 'Plugin Contents', '{project}', 'spt_plugin_content', 'pyasm.search.SObject', 'Plugin Contents', 'public');

INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/translation', 'config/translation', 'config', 'Translation', '{project}', 'spt_translation', 'pyasm.search.SObject', 'Translation', 'public');


