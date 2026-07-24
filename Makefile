PYTHON ?= python3
COMPOSE ?= docker compose
export PYTHONPATH := src
export SC_OFFLINE_LLM ?= 1

.PHONY: help setup test lint up down demo build-panel run-study validate eval scorecard-csv scorecard-seed

help:
	@echo "SimCrowd: setup test demo build-panel run-study validate eval"

setup:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests

build-panel:
	$(PYTHON) -m simcrowd.panel.cli --size $${SIZE:-200} --seed $${SEED:-42}

run-study:
	$(PYTHON) -m simcrowd.research.cli --spec $${SPEC:-data/concepts/fintech_survey.json} --panel $${PANEL:-artifacts/personas.jsonl}

validate:
	$(PYTHON) -m simcrowd.validation.pew_bench --panel $${PANEL:-artifacts/personas.jsonl}

eval:
	$(PYTHON) evals/run_evals.py --smoke $${SMOKE:-20}

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

demo: setup
	mkdir -p artifacts
	$(PYTHON) -m simcrowd.panel.cli --size 40 --seed 42 --out artifacts/personas.jsonl
	$(PYTHON) -m simcrowd.research.cli --spec data/concepts/fintech_survey.json --panel artifacts/personas.jsonl --out artifacts/study_fintech.json
	$(PYTHON) -m simcrowd.validation.pew_bench --panel artifacts/personas.jsonl --out artifacts/pew_scorecard.json
	$(PYTHON) evals/run_evals.py --smoke 20
	@echo "Demo artifacts in ./artifacts"


scorecard-seed:
	mkdir -p artifacts
	cp data/pew/sample_scorecard.json artifacts/pew_scorecard.json
	@echo "Seeded artifacts/pew_scorecard.json"


scorecard-csv:
	$(PYTHON) -m simcrowd.validation.pew_bench --panel $${PANEL:-artifacts/personas.jsonl} --out artifacts/pew_scorecard.json --csv artifacts/pew_scorecard.csv
	@echo "Wrote artifacts/pew_scorecard.csv"
