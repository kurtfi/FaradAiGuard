# FaradAiGuard 🛡️

**Open-source, zero-cost, multi-architecture Security SLM (Small Language Model) Factory for Agentic AI Gateways & PEP Systems.**

FaradAiGuard packages and serves calibrated security SLMs tailored for Policy Enforcement Points (like [FaradAiWire](https://github.com/kurtfi/FaradAiWire)). It converts, quantizes (Q4_K_M GGUF), and distributes models across:
1. **Hugging Face Hub (`faradailab`)**: Native Ollama-ready models (`hf.co/faradailab/guard-*`).
2. **GitHub Container Registry (`ghcr.io/kurtfi`)**: Standalone C++ `llama-server` multi-arch Docker images with strict GBNF grammar formatting.
3. **Apple Silicon / macOS MLX**: Native Metal-accelerated inference.

---

## 🎯 Supported Security Models & Paradigms

FaradAiGuard explicitly categorizes security models into two paradigms:
1. **Decision Models (`decision_model`)**: Encoder-only Sequence Classifiers (e.g., ModernBERT) evaluated via native Ollama `POST /v1/systemone` or `ollama run --ask`. They output calibrated probabilities without generative hallucination.
2. **Generative LLMs (`generative_llm`)**: Autoregressive Decoder LLMs evaluated via `POST /api/chat` or `POST /v1/chat/completions` with strict GBNF JSON grammar.

| Model | Paradigm | Architecture | Benchmark Acc. | FP Rate | RAM | PEP Endpoint |
|---|---|---|---|---|---|---|
| **Mica v0.5-4B** | `decision_model` | Qwen 4B (Saf) System 1 Decision Model | **87.1%** | **3.2%** | ~2.9 GB | Ollama `/v1/systemone`, `/api/generate`, Docker `:8088` |
| **Laya-Guard** | `decision_model` | ModernBERT (Sequence Classifier) | 86.2% | 4.4% | ~1.5 GB | Ollama `/v1/systemone`, `--ask` |
| **Perplexity Decider Flash** | `decision_model` | Qwen 3.5-4B Non-Autoregressive Head | 85.5% | 3.6% | ~2.0 GB | Ollama `/v1/systemone`, `/api/generate`, Docker `:8088` |
| **Liquid AI d1-3B** | `decision_model` | LFM Multimodal / Text Decision Head | 84.1% | 3.8% | ~2.3 GB | Ollama `/v1/systemone`, `/api/generate`, Docker `:8088` |
| **Qwen3Guard** | `generative_llm` | Qwen 2.5 (Autoregressive Decoder) | 79.6% | 3.3% | ~1 GB | Ollama `/api/chat`, Docker `:8088` |
| **Granite Guardian** | `generative_llm` | Granite 3.0 (Autoregressive Decoder) | 78.3% | 4.7% | ~2.5 GB | Ollama `/api/chat`, Docker `:8088` |

---

## 🚀 Quick Start

### Option 1: Native Ollama (Recommended for Local Dev)
Run models with Ollama (Metal GPU on macOS and CUDA on Linux supported out-of-the-box):

```bash
# Mica v0.5-4B (Saf System 1 Decision Model)
ollama run hf.co/faradailab/guard-mica

# Liquid AI d1-3B (Decision Model)
ollama run hf.co/faradailab/guard-liquid-d1

# Perplexity Decider Flash (Decision Model)
ollama run hf.co/faradailab/guard-pplx-decider

# Qwen3Guard (Generative LLM - Interactive chat)
ollama run hf.co/faradailab/guard-qwen3guard

# Laya-Guard (Decision Model - Single-turn evaluation via --ask or /v1/systemone)
ollama run hf.co/faradailab/guard-laya:latest --ask "PRIMARY_USER_GOAL: Inspect files\nTOOL_NAME: execute_bash\nCALL_ARGUMENTS: {\"cmd\":\"ls -la\"}"

# IBM Granite Guardian (Generative LLM - Interactive chat)
ollama run hf.co/faradailab/guard-granite
```

### Option 2: Docker Containers (Production & Cloud PEPs)
Run containerized C++ `llama-server` exposing OpenAI-compatible endpoints on port `8088`:

```bash
# Run Mica v0.5-4B Decision Model container
docker run -d --name faradai-guard-mica \
  -p 8088:8088 \
  ghcr.io/kurtfi/farad-ai-guard:mica-v0.5

# Run Liquid AI d1-3B Decision Model container
docker run -d --name faradai-guard-d1 \
  -p 8088:8088 \
  ghcr.io/kurtfi/farad-ai-guard:liquid-d1

# Run Perplexity Decider Flash container
docker run -d --name faradai-guard-pplx \
  -p 8088:8088 \
  ghcr.io/kurtfi/farad-ai-guard:pplx-decider

# Run Qwen3Guard container
docker run -d --name faradai-guard \
  -p 8088:8088 \
  ghcr.io/kurtfi/farad-ai-guard:qwen3guard

# Verify health
curl http://localhost:8088/health
```

### Option 3: Apple Silicon Mac (MLX)
For native Apple Silicon Metal acceleration using MLX:
```bash
pip install mlx-lm
python -m mlx_lm.generate --model faradailab/guard-laya-mlx --prompt "..."
```

---

## 📐 Strict Output Schema (GBNF Grammar)

FaradAiGuard enforces structured JSON output via llama.cpp GBNF grammar (`grammar/guard.gbnf`):

```json
{
  "verdict": "ALLOW",
  "risk_score": 0.05,
  "reason": "Safe directory listing tool invocation",
  "cwe": ""
}
```

```json
{
  "verdict": "BLOCK",
  "risk_score": 0.98,
  "reason": "Command injection detected attempting to read /etc/shadow",
  "cwe": "CWE-78"
}
```

---

## 🔄 FaradAiWire PEP Integration

[FaradAiWire](https://github.com/kurtfi/FaradAiWire) automatically discovers FaradAiGuard via `slmprobe`:
- Checks `:11434` (Ollama) and `:8088` (Docker) within **300ms**.
- If found, routes L2 semantic inspections via connection-pooled HTTP REST.
- If offline, falls back safely to L1 static regex rules without interrupting traffic.

---

## 🛠️ Build & Development

```bash
# Build Modelfile for Ollama
ollama create faradailab/guard-qwen3guard -f modelfiles/Modelfile.qwen3guard

# Build Docker image locally
docker build -t farad-ai-guard:qwen3guard -f docker/Dockerfile --build-arg MODEL=qwen3guard .
```

## 📜 License
Apache 2.0. Free for commercial and non-commercial use.
