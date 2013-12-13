

-- Note: this is still used on project creation.  DatabaseImpl uses this
-- to import the starting schema

CREATE TABLE spt_trigger (
    id INT IDENTITY PRIMARY KEY,
    code varchar(256),
    class_name varchar(256),
    script_path varchar(256),
    title varchar(256),
    description VARCHAR(MAX),
    event varchar(256),
    mode varchar(256),
    process varchar(256),
    listen_process varchar(256),
    trigger_type varchar(256),
    data VARCHAR(MAX),
    "timestamp" timestamp  DEFAULT now(),
    search_type varchar(256),
    s_status varchar(256),
    CONSTRAINT "spt_trigger_code_idx" UNIQUE (code)
);


CREATE TABLE widget_config (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    "view" character varying(256),
    category character varying(256),
    search_type character varying(256),
    "login" character varying(256),
    config VARCHAR(MAX),
    "timestamp" timestamp  DEFAULT now(),
    "widget_type" character varying(256),
    s_status character varying(32),
    CONSTRAINT "widget_config_code_idx" UNIQUE (code)
);


CREATE TABLE naming (
    id INT IDENTITY PRIMARY KEY,
    search_type character varying(100),
    dir_naming VARCHAR(MAX),
    file_naming VARCHAR(MAX),
    sandbox_dir_naming VARCHAR(MAX),
    snapshot_type character varying(256),
    context character varying(256),
    code character varying(256),
    latest_versionless boolean,
    current_versionless boolean,
    manual_version boolean,
    ingest_rule_code character varying(256),
    "condition" VARCHAR(MAX),
    class_name VARCHAR(MAX), 
    script_path VARCHAR(MAX),
    checkin_type character varying(256),
    CONSTRAINT "naming_code_idx" UNIQUE (code)
);



CREATE TABLE prod_setting (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    "key" character varying(100),
    value VARCHAR(MAX),
    description VARCHAR(MAX),
    "type" character varying(30),
    search_type character varying(200),
    category character varying(256),
    CONSTRAINT "prod_setting_code_idx" UNIQUE (code),
    CONSTRAINT "prod_setting_key_idx" UNIQUE ("key")
);



CREATE TABLE custom_script (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    title character varying(256),
    description VARCHAR(MAX),
    folder character varying(1024),
    script VARCHAR(MAX),
    "login" character varying(256),
    "timestamp" timestamp  DEFAULT now(),
    language character varying(256),
    s_status character varying(256),
    CONSTRAINT "custom_script_code_idx" UNIQUE (code)
);


CREATE TABLE spt_url (
    id INT IDENTITY PRIMARY KEY,
    code varchar(256),
    url varchar(256),
    widget VARCHAR(MAX),
    description VARCHAR(MAX),
    "timestamp" timestamp  DEFAULT now(),
    s_status varchar(256),
    CONSTRAINT "url_code_idx" UNIQUE (code)
);


CREATE TABLE spt_client_trigger (
    id INT IDENTITY PRIMARY KEY,
    code character varying(256),
    event character varying(256),
    callback character varying(256),
    description VARCHAR(MAX),
    "timestamp" timestamp  DEFAULT now(),
    s_status character varying(32),
    CONSTRAINT "client_trigger_code_idx" UNIQUE (code)
);



CREATE TABLE spt_process (
    id INT IDENTITY PRIMARY KEY,
    code varchar(256),
    pipeline_code varchar(256),
    process varchar(256),
    color varchar(256),
    sort_order integer,
    "timestamp" timestamp  DEFAULT now(),
    s_status varchar(256),
    checkin_mode VARCHAR(MAX), 
    subcontext_options VARCHAR(MAX), 
    checkin_validate_script_path VARCHAR(MAX), 
    checkin_options_view VARCHAR(MAX), 
    sandbox_create_script_path VARCHAR(MAX), 
    context_options VARCHAR(MAX), 
    description VARCHAR(MAX), 
    repo_type varchar(256), 
    transfer_mode varchar(256),
    CONSTRAINT "process_code_idx" UNIQUE (code)
);



CREATE TABLE spt_plugin (
    id INT IDENTITY PRIMARY KEY,
    code varchar(256),
    description VARCHAR(MAX),
    manifest VARCHAR(MAX),
    "timestamp" timestamp,
    version varchar(256),
    rel_dir VARCHAR(MAX),
    s_status varchar(256),
    CONSTRAINT "spt_plugin_code_idx" UNIQUE (code)
);



CREATE TABLE spt_pipeline (
    id INT IDENTITY PRIMARY KEY,
    code varchar(256),
    pipeline VARCHAR(MAX),
    "timestamp" timestamp DEFAULT now(),
    search_type varchar(256),
    description VARCHAR(MAX),
    s_status varchar(32),
    color character varying(256),
    autocreate_tasks boolean,
    CONSTRAINT "spt_pipeline_code_idx" UNIQUE (code)
);


