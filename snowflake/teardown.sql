-- Phase 2b: remove EVERYTHING created by setup.sql. Run before the trial ends.
-- Paste into a Snowsight worksheet as ACCOUNTADMIN → "Run All".
use role accountadmin;

drop user if exists health_svc;
drop database if exists health;           -- all schemas and tables inside it
drop warehouse if exists health_wh;
drop role if exists health_transformer;
drop resource monitor if exists health_trial_monitor;

-- Check: both should return no rows
show warehouses like 'HEALTH_WH';
show databases like 'HEALTH';
