# Every command for this project runs through these targets, inside Docker.
# `make help` lists them.

IMAGE := ee271-simd
PORT  ?= 8000

DOCKER_RUN := docker run --rm -v "$(CURDIR)":/work -w /work $(IMAGE)

.DEFAULT_GOAL := help
.PHONY: help build shell freeze starter-test test verify serve

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker build -f docker/Dockerfile -t $(IMAGE) .

shell: ## Open a shell in the container
	docker run --rm -it -v "$(CURDIR)":/work -w /work $(IMAGE) bash

freeze: ## Print installed package versions (for pinning requirements.txt)
	$(DOCKER_RUN) pip freeze

starter-test: ## Run the course's public tests (simd-part1/test), all of them
	$(DOCKER_RUN) make -k -C simd-part1/test run_tests

test: ## Run this repo's tests (visualizer, schema, server)
	$(DOCKER_RUN) python -m pytest -p no:cacheprovider tests

verify: test ## The gate: repo tests + validate every trace in traces/
	$(DOCKER_RUN) python -m viz.schema traces

serve: ## Run the visualizer at http://127.0.0.1:$(PORT)
	docker run --rm -it -p 127.0.0.1:$(PORT):8000 -v "$(CURDIR)":/work -w /work $(IMAGE) \
		python -m viz.server --host 0.0.0.0 --port 8000
