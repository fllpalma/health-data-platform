# Makefile: short commands for running the platform ON DEMAND (nothing runs unless started here).
# Usage: make up | make up-airflow | make down | make status
COMPOSE := docker compose --profile foundations --profile orchestration

.PHONY: up up-airflow down status

up:          ## Start the data platform only (lake + warehouse)
	docker compose --profile foundations up -d --wait

up-airflow:  ## Start data platform + Airflow (UI: http://localhost:8080)
	$(COMPOSE) up -d --wait

down:        ## Stop EVERYTHING (data is kept in volumes and data/)
	$(COMPOSE) stop

status:      ## Show what is running
	$(COMPOSE) ps -a --format "table {{.Service}}\t{{.State}}\t{{.Status}}"
