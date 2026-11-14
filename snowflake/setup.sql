-- Phase 2b: Snowflake trial setup (infrastructure as code).
-- Run ONCE in Snowsight as ACCOUNTADMIN: paste into a SQL worksheet → "Run All".
-- Replace <PUBLIC_KEY> with the body of ~/.snowflake/health_platform/rsa_key.pub (no header/footer lines).
-- Undo everything with snowflake/teardown.sql.

use role accountadmin;

-- 1) 💰 Budget alarm: a hard cap on credits. At 100% every warehouse on it is suspended immediately.
--    20 credits ≈ $60 of the $400 trial, plenty for an X-Small warehouse (1 credit per running hour).
create or replace resource monitor health_trial_monitor
with credit_quota = 20
frequency = never
start_timestamp = immediately
triggers
on 50 percent do notify
on 80 percent do notify
on 100 percent do suspend_immediate;

-- 2) 🔥 The stove: smallest size, switches itself off after 60 s idle, on again when a query arrives.
create warehouse if not exists health_wh
with warehouse_size = xsmall
auto_suspend = 60
auto_resume = true
initially_suspended = true
resource_monitor = health_trial_monitor
comment = 'Phase 2b: dbt + dlt (trial)';

-- 3) 🗄️ The database. dlt and dbt create their own schemas inside it (raw_apple_health, staging, ...).
create database if not exists health comment = 'Phase 2b: synthetic data + optional daily summaries only';

-- 4) 🔑 A role with only what's needed (least privilege).
create role if not exists health_transformer;
grant usage, operate on warehouse health_wh to role health_transformer;
grant usage, create schema on database health to role health_transformer;
grant role health_transformer to role sysadmin;  -- lets admins see what it creates

-- 5) 🤖 A service user for dbt/dlt: key-pair login only, no password, can't log into the web UI.
create user if not exists health_svc
type = service
default_role = health_transformer
default_warehouse = health_wh
rsa_public_key = '<PUBLIC_KEY>'
comment = 'dbt + dlt service user (key-pair auth)';
grant role health_transformer to user health_svc;

-- Check: should show XSMALL, 60, HEALTH_TRIAL_MONITOR
show warehouses like 'HEALTH_WH';
