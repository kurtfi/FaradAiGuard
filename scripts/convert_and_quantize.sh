#!/usr/bin/env bash
# Conversion and Q4_K_M quantization pipeline for FaradAiGuard models
set -euo pipefail

MODEL_ID="${1:-Qwen/Qwen2.5-0.5B-Instruct}"
OUTPUT_NAME="${2:-qwen3guard}"
QUANT_TYPE="${3:-q4_k_m}"

echo "=== FaradAiGuard Quantization Pipeline ==="
echo "Source: ${MODEL_ID}"
echo "Target: ${OUTPUT_NAME} (${QUANT_TYPE})"

WORKDIR="./build/${OUTPUT_NAME}"
mkdir -p "${WORKDIR}"

# 1. Download HF model weights
echo "[1/3] Downloading model weights from Hugging Face..."
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='${MODEL_ID}', local_dir='${WORKDIR}/hf_raw')
"

# 2. Convert to FP16 GGUF using llama.cpp convert-hf-to-gguf.py
echo "[2/3] Converting to GGUF FP16..."
python3 llama.cpp/convert_hf_to_gguf.py "${WORKDIR}/hf_raw" --outfile "${WORKDIR}/${OUTPUT_NAME}-f16.gguf"

# 3. Quantize to target format
echo "[3/3] Quantizing to ${QUANT_TYPE}..."
llama.cpp/llama-quantize "${WORKDIR}/${OUTPUT_NAME}-f16.gguf" "${WORKDIR}/${OUTPUT_NAME}-${QUANT_TYPE}.gguf" "${QUANT_TYPE}"

echo "Quantization complete: ${WORKDIR}/${OUTPUT_NAME}-${QUANT_TYPE}.gguf"
