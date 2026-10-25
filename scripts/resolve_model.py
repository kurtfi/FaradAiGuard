#!/usr/bin/env python3
"""
FaradAiGuard: Platform-Aware Model & Runtime Resolver
Automatically detects hardware environment (Apple Silicon Metal vs Linux/CUDA vs Container)
and routes to the optimal format:
  - Apple Silicon Mac (MLX mode): faradailab/guard-<model>-mlx
  - Universal (Ollama mode): hf.co/faradailab/guard-<model>:latest (runs Metal on Mac, CUDA on Linux)
  - Container / Cloud PEP: ghcr.io/kurtfi/farad-ai-guard:<model>
"""

import argparse
import platform
import subprocess
import sys
from typing import Dict, Any


def detect_environment() -> Dict[str, Any]:
    os_name = platform.system()
    arch = platform.machine()
    is_mac = os_name == "Darwin"
    is_apple_silicon = is_mac and arch in ("arm64", "aarch64")

    has_cuda = False
    try:
        res = subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        has_cuda = (res.returncode == 0)
    except FileNotFoundError:
        has_cuda = False

    return {
        "os": os_name,
        "arch": arch,
        "is_apple_silicon": is_apple_silicon,
        "has_cuda": has_cuda,
        "recommended_accelerator": "Metal (Apple Silicon)" if is_apple_silicon else ("CUDA (NVIDIA)" if has_cuda else "CPU"),
    }


def resolve_model(model_name: str = "laya", target_runtime: str = "auto") -> Dict[str, str]:
    """
    Resolves the exact model repository and command based on hardware, runtime preference,
    and architectural model paradigm (Generative LLM vs Decision Model).
    """
    env = detect_environment()

    # Architectural model paradigm
    is_decision_model = (model_name == "laya")
    paradigm_str = "Decision Model (ModernBERT Encoder, /v1/systemone)" if is_decision_model else "Generative LLM (Autoregressive, /api/chat)"

    # Determine runtime if 'auto'
    if target_runtime == "auto":
        # Default to Ollama since Ollama supports Metal on Apple Silicon natively and CUDA on Linux
        chosen_runtime = "ollama"
    else:
        chosen_runtime = target_runtime.lower()

    if chosen_runtime == "mlx":
        if not env["is_apple_silicon"]:
            print("⚠️ Warning: MLX is optimized specifically for Apple Silicon macOS. Falling back to Ollama.")
            chosen_runtime = "ollama"
        else:
            model_id = f"faradailab/guard-{model_name}-mlx"
            cmd = f"python -m mlx_lm.generate --model {model_id} --prompt '...'"
            return {
                "paradigm": paradigm_str,
                "runtime": "MLX (Apple Silicon Metal)",
                "model_id": model_id,
                "command": cmd,
                "environment": env["recommended_accelerator"],
            }

    if chosen_runtime == "docker":
        model_id = f"ghcr.io/kurtfi/farad-ai-guard:{model_name}"
        cmd = f"docker run -d -p 8088:8088 {model_id}"
        return {
            "paradigm": paradigm_str,
            "runtime": "Docker (llama-server)",
            "model_id": model_id,
            "command": cmd,
            "environment": env["recommended_accelerator"],
        }

    # Default: Ollama (runs Metal on Mac, CUDA on Linux)
    model_id = f"hf.co/faradailab/guard-{model_name}:latest"
    if is_decision_model:
        cmd = f"ollama run {model_id} --ask 'PRIMARY_USER_GOAL: ...'"
    else:
        cmd = f"ollama run {model_id}"
    return {
        "paradigm": paradigm_str,
        "runtime": f"Ollama ({env['recommended_accelerator']})",
        "model_id": model_id,
        "command": cmd,
        "environment": env["recommended_accelerator"],
    }


def main():
    parser = argparse.ArgumentParser(description="Resolve optimal FaradAiGuard model and runtime for this machine.")
    parser.add_argument("--model", default="laya", choices=["qwen3guard", "laya", "granite"], help="Model name")
    parser.add_argument(
        "--runtime",
        default="auto",
        choices=["auto", "ollama", "mlx", "docker"],
        help="Target runtime: auto (recommended), ollama (native GPU), mlx (macOS Apple Silicon), docker",
    )
    parser.add_argument("--execute", action="store_true", help="Directly execute the recommended command")
    args = parser.parse_args()

    env = detect_environment()
    res = resolve_model(args.model, args.runtime)

    print("=== FaradAiGuard Hardware & Model Resolution ===")
    print(f"  OS / Architecture : {env['os']} ({env['arch']})")
    print(f"  Apple Silicon     : {'Yes (Native Metal GPU)' if env['is_apple_silicon'] else 'No'}")
    print(f"  NVIDIA CUDA       : {'Yes' if env['has_cuda'] else 'No'}")
    print(f"  Optimal Backend   : {res['environment']}")
    print("------------------------------------------------")
    print(f"  Model Paradigm    : {res['paradigm']}")
    print(f"  Target Runtime    : {res['runtime']}")
    print(f"  Model ID          : {res['model_id']}")
    print(f"  Launch Command    : {res['command']}")
    print("================================================")

    if args.execute:
        print(f"\n🚀 Launching: {res['command']}\n")
        subprocess.run(res['command'], shell=True)


if __name__ == "__main__":
    main()
