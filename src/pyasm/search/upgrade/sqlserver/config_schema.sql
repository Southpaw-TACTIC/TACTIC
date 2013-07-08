SET QUOTED_IDENTIFIER ON;


-- Note: this is still used on project creation.  DatabaseImpl uses this
-- to import the starting schema

CREATE TABLE spt_trigger (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    class_name nvarchar(256),
    script_path nvarchar(256),
    title nvarchar(256),
    description nvarchar(max),
    event nvarchar(256),
    mode nvarchar(256),
    process nvarchar(256),
    listen_process nvarchar(256),
    trigger_type nvarchar(256),
    data nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    search_type nvarchar(256),
    s_status nvarchar(256),
    CONSTRAINT "spt_trigger_code_idx" UNIQUE (code)
);


CREATE TABLE widget_config (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    "view" nvarchar(256),
    category nvarchar(256),
    search_type nvarchar(256),
    "login" nvarchar(256),
    config nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    "widget_type" nvarchar(256),
    s_status nvarchar(32),
    CONSTRAINT "widget_config_code_idx" UNIQUE (code)
);


CREATE TABLE naming (
    id integer IDENTITY PRIMARY KEY,
    search_type nvarchar(100),
    dir_naming nvarchar(max),
    file_naming nvarchar(max),
    sandbox_dir_naming nvarchar(max),
    snapshot_type nvarchar(256),
    context nvarchar(256),
    code nvarchar(256),
    latest_versionless BIT,
    current_versionless BIT,
    manual_version BIT,
    ingest_rule_code nvarchar(256),
    "condition" nvarchar(max),
    class_name nvarchar(max), 
    script_path nvarchar(max),
    checkin_type nvarchar(256),
    CONSTRAINT "naming_code_idx" UNIQUE (code)
);



CREATE TABLE prod_setting (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    "key" nvarchar(100),
    value nvarchar(max),
    description nvarchar(max),
    "type" nvarchar(30),
    search_type nvarchar(200),
    category nvarchar(256),
    CONSTRAINT "prod_setting_code_idx" UNIQUE (code),
    CONSTRAINT "prod_setting_key_idx" UNIQUE ("key")
);



CREATE TABLE custom_script (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    title nvarchar(256),
    description nvarchar(max),
    folder nvarchar(1024),
    script nvarchar(max),
    "login" nvarchar(256),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    language nvarchar(256),
    s_status nvarchar(256),
    CONSTRAINT "custom_script_code_idx" UNIQUE (code)
);


CREATE TABLE spt_url (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    url nvarchar(256),
    widget nvarchar(max),
    description nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    s_status nvarchar(256),
    CONSTRAINT "url_code_idx" UNIQUE (code)
);


CREATE TABLE spt_client_trigger (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    event nvarchar(256),
    callback nvarchar(256),
    description nvarchar(max),
    "timestamp" datetime2(6) DEFAULT (getdate()),
    s_status nvarchar(32),
    CONSTRAINT "client_trigger_code_idx" UNIQUE (code)
);



CREATE TABLE spt_process (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    pipeline_code nvarchar(256),
    process nvarchar(256),
    color nvarchar(256),
    sort_order integer,
    "timestamp" datetime2(6) DEFAULT (getdate()),
    s_status nvarchar(256),
    checkin_mode nvarchar(max), 
    subcontext_options nvarchar(max), 
    checkin_validate_script_path nvarchar(max), 
    checkin_options_view nvarchar(max), 
    sandbox_create_script_path nvarchar(max), 
    context_options nvarchar(max), 
    description nvarchar(max), 
    repo_type nvarchar(256), 
    transfer_mode nvarchar(256),
    CONSTRAINT "process_code_idx" UNIQUE (code)
);



CREATE TABLE spt_plugin (
    id integer IDENTITY PRIMARY KEY,
    code nvarchar(256),
    description nvarchar(max),
    manifest nvarchar(max),
    datetime2(6) datetime2(6),
    version nvarchar(256),
    rel_dir nvarchar(max),
    s_status nvarchar(256),
    CONSTRAINT "spt_plugin_code_idx" UNIQUE (code)
)

