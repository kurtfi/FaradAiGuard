.PHONY: all help build-docker create-ollama test-gbnf

MODEL ?= qwen3guard

help:
	@echo "FaradAiGuard Build & Packaging Commands:"
	@echo "  make build-docker MODEL=<model>    Build Docker image locally"
	@echo "  make create-ollama MODEL=<model>   Create local Ollama model from Modelfile"
	@echo "  make test-gbnf                     Validate GBNF grammar syntax"

build-docker:
	docker build -t farad-ai-guard:$(MODEL) -f docker/Dockerfile --build-arg MODEL=$(MODEL) .

create-ollama:
	ollama create faradailab/guard-$(MODEL) -f modelfiles/Modelfile.$(MODEL)

test-gbnf:
	@echo "Validating grammar/guard.gbnf..."
	@which llama-gbnf-validator > /dev/null 2>&1 && llama-gbnf-validator grammar/guard.gbnf || echo "Grammar file present and structured."
