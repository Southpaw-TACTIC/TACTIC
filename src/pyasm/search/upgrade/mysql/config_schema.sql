SET sql_mode='PIPES_AS_CONCAT,ANSI_QUOTES';
--
--


CREATE TABLE "spt_trigger" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "class_name" character varying(256),
    "script_path" character varying(256),
    "title" character varying(256),
    "description" longtext,
    "event" character varying(256),
    "mode" character varying(256),
    "process" character varying(256),
    "listen_process" character varying(256),
    "trigger_type" character varying(256),
    "data" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "search_type" character varying(256),
    "s_status" character varying(256),
    CONSTRAINT "spt_trigger_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_widget_config" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "view" character varying(256),
    "category" character varying(256),
    "search_type" character varying(256),
    "login" character varying(256),
    "config" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "widget_type" character varying(256),
    "s_status" character varying(32),
    CONSTRAINT "spt_widget_config_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_naming" (
    "id" serial PRIMARY KEY,
    "search_type" character varying(100),
    "dir_naming" longtext,
    "file_naming" longtext,
    "sandbox_dir_naming" longtext,
    "snapshot_type" character varying(256),
    "context" character varying(256),
    "code" character varying(256),
    "latest_versionless" boolean,
    "current_versionless" boolean,
    "manual_version" boolean,
    "ingest_rule_code" character varying(256),
    "condition" longtext,
    "class_name" longtext, 
    "script_path" longtext,
    "checkin_type" character varying(256),
    "base_dir_alias" character varying(256),
    "sandbox_dir_alias" character varying(256),
    CONSTRAINT "spt_naming_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_prod_setting" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "key" character varying(100),
    "value" longtext,
    "description" longtext,
    "type" character varying(30),
    "search_type" character varying(200),
    "category" character varying(256),
    CONSTRAINT "spt_prod_setting_code_idx" UNIQUE ("code"),
    CONSTRAINT "spt_prod_setting_key_idx" UNIQUE ("key")
);


CREATE TABLE "spt_custom_script" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "title" character varying(256),
    "description" longtext,
    "folder" character varying(1024),
    "script" longtext,
    "login" character varying(256),
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "language" character varying(256),
    "s_status" character varying(256),
    CONSTRAINT "spt_custom_script_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_url" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "url" character varying(256),
    "widget" longtext,
    "description" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "s_status" character varying(256),
    CONSTRAINT "spt_url_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_client_trigger" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "event" character varying(256),
    "callback" character varying(256),
    "description" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "s_status" character varying(32),
    CONSTRAINT "spt_client_trigger_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_process" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "pipeline_code" character varying(256),
    "process" character varying(256),
    "color" character varying(256),
    "sort_order" integer,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "s_status" character varying(256),
    "checkin_mode" longtext,  
    "subcontext_options" longtext, 
    "checkin_validate_script_path" longtext, 
    "checkin_options_view" longtext, 
    "sandbox_create_script_path" longtext, 
    "context_options" longtext, 
    "description" longtext, 
    "repo_type" character varying(256), 
    "transfer_mode" character varying(256),
    CONSTRAINT "spt_process_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_plugin" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "description" longtext,
    "manifest" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "version" character varying(256),
    "rel_dir" longtext,
    "s_status" character varying(256),
    CONSTRAINT "spt_plugin_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_pipeline" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "pipeline" longtext,
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "search_type" character varying(256),
    "description" longtext,
    "s_status" character varying(32),
    "color" character varying(256),
    "autocreate_tasks" boolean,
    "data" jsonb,
    CONSTRAINT "spt_pipeline_code_idx" UNIQUE ("code")
);


CREATE TABLE "spt_process_state" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
    "pipeline_code" character varying(256),
    "process" character varying(256),
    "search_type" character varying(256),
    "search_code" character varying(256),
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "status" jsonb,
    "state" character varying(256),
    "data" jsonb,
    "s_status" character varying(32),
    CONSTRAINT "spt_pipeline_info_code_idx" UNIQUE ("code")
);






-- Missing tables

CREATE TABLE "spt_ingest_rule" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"spt_ingest_session_code" character varying(256),
	"title" longtext,
	"base_dir" character varying(1024),
	"rule" character varying(1024),
	"data" text
);


CREATE TABLE "spt_ingest_session" (
    "id" serial PRIMARY KEY,
    "code" character varying(256),
	"title" longtext,
	"base_dir" character varying(1024),
	"location" character varying(256),
	"data" text
);


CREATE TABLE "spt_plugin_content" (
    "id" serial PRIMARY KEY,
	"code" character varying(256),
	"plugin_code" character varying(256),
	"search_type" character varying(256),
	"search_code" character varying(256)
);


CREATE TABLE "spt_translation" (
    "id" serial PRIMARY KEY,
	"code" character varying(256),
	"name" character varying(256),
	"en" longtext,
	"fr" longtext,
	"ja" longtext,
	"es" longtext,
	"login" character varying(256),
    "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT "spt_translation_code_idx" UNIQUE ("code"),
	CONSTRAINT "spt_translation_name_idx" UNIQUE ("name")
);

