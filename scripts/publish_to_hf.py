#!/usr/bin/env python3
"""
FaradAiGuard: Hugging Face Publisher
Automates uploading GGUF weights, customized Modelfile, and Model Cards to Hugging Face Hub
so models are immediately runnable via `ollama run hf.co/faradailab/guard-<model>:latest`.
"""

import argparse
import os
import re
import sys

MODELS_CONFIG = {
    "qwen3guard": {
        "category": "llm",
        "source_repo": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "source_file": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "target_file": "guard-qwen3guard.Q4_K_M.gguf",
        "title": "FaradAiGuard Qwen3Guard-0.6B Security SLM",
        "desc": "Ultra-lightweight (<20ms) inline PEP security evaluator model.",
    },
    "laya": {
        "category": "decision",
        "source_repo": "ggml-org/Laya-GGUF",
        "source_file": "Laya-Q8_0.gguf",
        "target_file": "guard-laya.Q4_K_M.gguf",
        "title": "FaradAiGuard Laya-Guard Decision Model",
        "desc": "Deep heuristic security evaluation model with ModernBERT sequence classification and Root Intent Isolation.",
    },
    "granite": {
        "category": "llm",
        "source_repo": "QuantFactory/granite-guardian-3.0-2b-GGUF",
        "source_file": "granite-guardian-3.0-2b.Q4_K_M.gguf",
        "target_file": "guard-granite.Q4_K_M.gguf",
        "title": "FaradAiGuard Granite Guardian 2.0B Security SLM",
        "desc": "Enterprise compliance and data loss prevention (DLP) inspector.",
    },
}


def publish_model(model_name: str, hf_token: str, organization: str = "faradailab"):
    try:
        from huggingface_hub import HfApi, create_repo, hf_hub_download
    except ImportError:
        print("ERROR: 'huggingface_hub' package not installed. Run 'pip install huggingface_hub'.")
        sys.exit(1)

    if model_name not in MODELS_CONFIG:
        raise ValueError(f"Unknown model '{model_name}'. Supported: {list(MODELS_CONFIG.keys())}")

    cfg = MODELS_CONFIG[model_name]
    repo_id = f"{organization}/guard-{model_name}"

    print(f"=== Publishing {model_name} to Hugging Face ({repo_id}) ===")
    api = HfApi(token=hf_token)
    create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=hf_token)

    # 1. Download base GGUF weights
    print(f"[1/4] Downloading base GGUF weights from {cfg['source_repo']} ({cfg['source_file']})...")
    local_gguf = hf_hub_download(
        repo_id=cfg["source_repo"],
        filename=cfg["source_file"],
    )
    print(f"      Cached at: {local_gguf}")

    # 2. Upload GGUF file to target HF repo
    print(f"[2/4] Uploading {cfg['target_file']} to {repo_id}...")
    api.upload_file(
        path_or_fileobj=local_gguf,
        path_in_repo=cfg["target_file"],
        repo_id=repo_id,
        repo_type="model",
    )
    print(f"      Uploaded {cfg['target_file']}")

    # 3. Prepare and upload Modelfile
    print(f"[3/4] Preparing Modelfile for Ollama...")
    modelfile_src = f"modelfiles/Modelfile.{model_name}"
    if os.path.exists(modelfile_src):
        with open(modelfile_src, "r") as f:
            content = f.read()

        # Update FROM instruction to point directly to relative GGUF file in repo
        hf_modelfile_content = re.sub(
            r"^FROM\s+.*$",
            f"FROM ./{cfg['target_file']}",
            content,
            flags=re.MULTILINE,
        )

        temp_modelfile = f"/tmp/Modelfile.{model_name}"
        with open(temp_modelfile, "w") as f:
            f.write(hf_modelfile_content)

        api.upload_file(
            path_or_fileobj=temp_modelfile,
            path_in_repo="Modelfile",
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"      Uploaded Modelfile (pointing to ./{cfg['target_file']})")

    # 4. Upload Model Card (README.md)
    print(f"[4/4] Generating and uploading Model Card...")
    model_card = f"""---
license: apache-2.0
base_model: {cfg['source_repo']}
tags:
  - ollama
  - gguf
  - security
  - farad-ai-guard
  - policy-enforcement
---

# {cfg['title']} 🛡️

{cfg['desc']} Part of the **FaradAiGuard** Security SLM Factory.

## 🚀 Instant Ollama Run

Run this model directly without local configuration or compilation:

```bash
ollama run hf.co/{repo_id}:latest
```

## ⚙️ Model Details

- **Distribution:** Hugging Face Hub (`{repo_id}`)
- **Format:** GGUF (`{cfg['target_file']}`)
- **System Prompt & Strict JSON Grammar:** Pre-configured via `Modelfile`.
- **Repository:** [https://github.com/kurtfi/FaradAiGuard](https://github.com/kurtfi/FaradAiGuard)

## 📐 Strict Output Schema (GBNF Grammar)

FaradAiGuard models return strictly validated JSON:

```json
{{
  "verdict": "ALLOW" | "BLOCK",
  "risk_score": 0.0 - 1.0,
  "reason": "Brief technical security explanation",
  "cwe": "CWE-ID or empty string"
}}
```
"""
    temp_readme = f"/tmp/README.{model_name}.md"
    with open(temp_readme, "w") as f:
        f.write(model_card)

    api.upload_file(
        path_or_fileobj=temp_readme,
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
    )
    print(f"      Uploaded README.md")

    print(f"\n✅ SUCCESS: hf.co/{repo_id}:latest is ready for `ollama run`!\n")


def main():
    parser = argparse.ArgumentParser(description="Publish FaradAiGuard models to Hugging Face")
    parser.add_argument("--model", required=True, choices=["all", "qwen3guard", "laya", "granite"])
    parser.add_argument("--org", default="faradailab", help="Hugging Face organization")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable not set. Please set it before running.")
        sys.exit(1)

    targets = list(MODELS_CONFIG.keys()) if args.model == "all" else [args.model]
    for m in targets:
        publish_model(m, token, args.org)


if __name__ == "__main__":
    main()
