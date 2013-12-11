

-- Note: this is still used on project creation.  DatabaseImpl uses this
-- to import the starting schema

CREATE TABLE spt_trigger (
    id serial PRIMARY KEY,
    code varchar(256),
    class_name varchar(256),
    script_path varchar(256),
    title varchar(256),
    description text,
    event varchar(256),
    mode varchar(256),
    process varchar(256),
    listen_process varchar(256),
    trigger_type varchar(256),
    data text,
    "timestamp" timestamp without time zone DEFAULT now(),
    search_type varchar(256),
    s_status varchar(256),
    CONSTRAINT "spt_trigger_code_idx" UNIQUE (code)
);


CREATE TABLE widget_config (
    id serial PRIMARY KEY,
    code character varying(256),
    "view" character varying(256),
    category character varying(256),
    search_type character varying(256),
    "login" character varying(256),
    config text,
    "timestamp" timestamp without time zone DEFAULT now(),
    "widget_type" character varying(256),
    s_status character varying(32),
    CONSTRAINT "widget_config_code_idx" UNIQUE (code)
);


CREATE TABLE naming (
    id serial PRIMARY KEY,
    search_type character varying(100),
    dir_naming text,
    file_naming text,
    sandbox_dir_naming text,
    snapshot_type character varying(256),
    context character varying(256),
    code character varying(256),
    latest_versionless boolean,
    current_versionless boolean,
    manual_version boolean,
    ingest_rule_code character varying(256),
    "condition" text,
    class_name text, 
    script_path text,
    checkin_type character varying(256),
    CONSTRAINT "naming_code_idx" UNIQUE (code)
);



CREATE TABLE prod_setting (
    id serial PRIMARY KEY,
    code character varying(256),
    "key" character varying(100),
    value text,
    description text,
    "type" character varying(30),
    search_type character varying(200),
    category character varying(256),
    CONSTRAINT "prod_setting_code_idx" UNIQUE (code),
    CONSTRAINT "prod_setting_key_idx" UNIQUE ("key")
);



CREATE TABLE custom_script (
    id serial PRIMARY KEY,
    code character varying(256),
    title character varying(256),
    description text,
    folder character varying(1024),
    script text,
    "login" character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    language character varying(256),
    s_status character varying(256),
    CONSTRAINT "custom_script_code_idx" UNIQUE (code)
);


CREATE TABLE spt_url (
    id serial PRIMARY KEY,
    code varchar(256),
    url varchar(256),
    widget text,
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status varchar(256),
    CONSTRAINT "url_code_idx" UNIQUE (code)
);


CREATE TABLE spt_client_trigger (
    id serial PRIMARY KEY,
    code character varying(256),
    event character varying(256),
    callback character varying(256),
    description text,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status character varying(32),
    CONSTRAINT "client_trigger_code_idx" UNIQUE (code)
);



CREATE TABLE spt_process (
    id serial PRIMARY KEY,
    code varchar(256),
    pipeline_code varchar(256),
    process varchar(256),
    color varchar(256),
    sort_order integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    s_status varchar(256),
    checkin_mode text, 
    subcontext_options text, 
    checkin_validate_script_path text, 
    checkin_options_view text, 
    sandbox_create_script_path text, 
    context_options text, 
    description text, 
    repo_type varchar(256), 
    transfer_mode varchar(256),
    CONSTRAINT "process_code_idx" UNIQUE (code)
);



CREATE TABLE spt_plugin (
    id serial PRIMARY KEY,
    code varchar(256),
    description text,
    manifest text,
    "timestamp" timestamp,
    version varchar(256),
    rel_dir text,
    s_status varchar(256),
    CONSTRAINT "spt_plugin_code_idx" UNIQUE (code)
);

