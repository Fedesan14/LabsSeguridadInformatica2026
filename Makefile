# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# CyberLab UTN — orquestación de entornos Docker.
# Uso rápido:
#   make setup          construye la consola del atacante (una sola vez)
#   make lab N=05       levanta el entorno del lab 05 (atacante + target)
#   make shell          entra a la consola del atacante
#   make down           baja los contenedores
#   make ps / make clean

SHELL := /bin/bash
PROJECT := cyberlab
DCFLAGS := --project-directory .
BASE := entorno/docker-compose.yml
N ?=

# Resuelve el compose del target del lab N (labs/labNN-*/entorno/target.compose.yml)
define lab_compose
$(firstword $(wildcard labs/lab$(N)-*/entorno/target.compose.yml))
endef

.PHONY: setup lab shell shell-victima down ps clean help
help:
	@echo "make setup        · construye la consola del atacante"
	@echo "make lab N=05     · levanta atacante + target del lab 05"
	@echo "make shell        · entra a la consola del atacante"
	@echo "make shell-victima · entra al host comprometido (Lab 08)"
	@echo "make down         · baja todo"
	@echo "make ps / clean"

setup:
	docker compose -p $(PROJECT) $(DCFLAGS) -f $(BASE) build attacker
	@echo "Listo. Ahora:  make lab N=05"

lab:
	@if [ -z "$(N)" ]; then echo "Falta el número de lab. Ej: make lab N=05"; exit 1; fi
	@if [ -z "$(strip $(lab_compose))" ]; then echo "El lab $(N) no tiene entorno Docker (target.compose.yml)."; exit 1; fi
	docker compose -p $(PROJECT) $(DCFLAGS) -f $(BASE) -f $(lab_compose) up -d --build
	@echo ""
	@echo ">> Entorno del lab $(N) arriba. Entrá con:  make shell"

shell:
	docker exec -e LLM_PROVIDER -e LLM_MODEL -e ANTHROPIC_API_KEY -e OPENAI_API_KEY -it $(PROJECT)-attacker bash || \
	  echo "No hay consola corriendo. Levantá un lab primero:  make lab N=05"

shell-victima:
	docker exec -u operador -it cyberlab-phantomcorp bash || \
	  echo "No hay host comprometido. Es del Lab 08:  make lab N=08"

down:
	docker compose -p $(PROJECT) $(DCFLAGS) -f $(BASE) $(if $(strip $(lab_compose)),-f $(lab_compose),) down

ps:
	docker compose -p $(PROJECT) ps

clean:
	docker compose -p $(PROJECT) $(DCFLAGS) -f $(BASE) down -v --remove-orphans 2>/dev/null || true
	@echo "Entorno limpio."
