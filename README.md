# FaradAiGuard 🛡️

**Open-source, zero-cost, multi-architecture Security SLM (Small Language Model) Factory for Agentic AI Gateways & PEP Systems.**

FaradAiGuard packages and serves calibrated security SLMs tailored for Policy Enforcement Points (like [FaradAiWire](https://github.com/kurtfi/FaradAiWire)). It converts, quantizes (Q4_K_M GGUF), and distributes models across:
1. **Hugging Face Hub (`faradailab`)**: Native Ollama-ready models (`hf.co/faradailab/guard-*`).
2. **GitHub Container Registry (`ghcr.io/kurtfi`)**: Standalone C++ `llama-server` multi-arch Docker images with strict GBNF grammar formatting.
3. **Apple Silicon / macOS MLX**: Native Metal-accelerated inference.

---

## 🎯 Supported Security Models

| Model | Parameters | Benchmark Accuracy | False Positive | RAM | Best For |
|---|---|---|---|---|---|
| **Qwen3Guard** | 0.6B | 79.6% | **3.3%** | ~1 GB | Fast developer workstations, low latency (<20ms) |
| **Kaya-Guard** | ~1.5B | **86.2%** | 4.4% | ~1.5 GB | Deep threat detection, agent-to-agent prompt injection |
| **Granite Guardian** | 2.0B | 78.3% | 4.7% | ~2.5 GB | Enterprise compliance, DLP, and OWASP Top 10 |

---

## 🚀 Quick Start

### Option 1: Native Ollama (Recommended for Local Dev)
Run any model instantly with Ollama (Metal GPU on macOS and CUDA on Linux supported out-of-the-box):

```bash
# Qwen3Guard (Ultra-lightweight)
ollama run hf.co/faradailab/guard-qwen3guard

# Kaya-Guard (Deep Security)
ollama run hf.co/faradailab/guard-kaya

# IBM Granite Guardian
ollama run hf.co/faradailab/guard-granite
```

### Option 2: Docker Containers (Production & Cloud PEPs)
Run containerized C++ `llama-server` exposing OpenAI-compatible endpoints on port `8088`:

```bash
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
python -m mlx_lm.generate --model faradailab/guard-kaya-mlx --prompt "..."
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
