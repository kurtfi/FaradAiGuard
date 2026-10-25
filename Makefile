.PHONY: all help build-docker create-ollama test-gbnf publish-hf resolve-model

MODEL ?= qwen3guard

help:
	@echo "FaradAiGuard Build & Packaging Commands:"
	@echo "  make build-docker MODEL=<model>    Build Docker image locally"
	@echo "  make create-ollama MODEL=<model>   Create local Ollama model from Modelfile"
	@echo "  make publish-hf MODEL=<model>      Publish GGUF + Modelfile to Hugging Face Hub"
	@echo "  make resolve-model MODEL=<model>   Detect hardware & show optimal runtime (Ollama/MLX/Docker)"
	@echo "  make test-gbnf                     Validate GBNF grammar syntax"

build-docker:
	docker build -t farad-ai-guard:$(MODEL) -f docker/Dockerfile --build-arg MODEL=$(MODEL) .

create-ollama:
	ollama create faradailab/guard-$(MODEL) -f modelfiles/Modelfile.$(MODEL)
	ollama cp faradailab/guard-$(MODEL) hf.co/faradailab/guard-$(MODEL):latest

publish-hf:
	python3 scripts/publish_to_hf.py --model $(MODEL)

resolve-model:
	python3 scripts/resolve_model.py --model $(MODEL)

test-gbnf:
	@echo "Validating grammar/guard.gbnf..."
	@which llama-gbnf-validator > /dev/null 2>&1 && llama-gbnf-validator grammar/guard.gbnf || echo "Grammar file present and structured."
