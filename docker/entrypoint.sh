#!/bin/sh
set -e

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8088}"
CTX_SIZE="${CTX_SIZE:-4096}"
MODEL_NAME="${MODEL_NAME:-qwen3guard}"
MODEL_FILE="/models/${MODEL_NAME}.gguf"
FLASH_ATTN="${FLASH_ATTN:-auto}"

echo "=== FaradAiGuard C++ PEP Inference Server ==="
echo "  Host         : ${HOST}"
echo "  Port         : ${PORT}"
echo "  Context Size : ${CTX_SIZE}"
echo "  Target Model : ${MODEL_NAME}"
echo "  Flash Attn   : ${FLASH_ATTN}"

# Model resolution strategy:
# 1. Local/Baked file: /models/${MODEL_NAME}.gguf
# 2. Explicit GGUF_PATH environment variable
# 3. Direct Hugging Face streaming via --hf-repo / --hf-file (HF_REPO / HF_FILE)
# 4. Known default HF repos for FaradAiGuard models

if [ -n "${GGUF_PATH}" ] && [ -f "${GGUF_PATH}" ]; then
    echo "  Loading from GGUF_PATH: ${GGUF_PATH}"
    TARGET_ARG="--model ${GGUF_PATH}"
elif [ -f "${MODEL_FILE}" ]; then
    echo "  Loading from baked/mounted model: ${MODEL_FILE}"
    TARGET_ARG="--model ${MODEL_FILE}"
elif [ -n "${HF_REPO}" ]; then
    if [ -n "${HF_FILE}" ]; then
        echo "  Loading from Hugging Face: ${HF_REPO} (${HF_FILE})"
        TARGET_ARG="--hf-repo ${HF_REPO} --hf-file ${HF_FILE}"
    else
        echo "  Loading from Hugging Face: ${HF_REPO}"
        TARGET_ARG="--hf-repo ${HF_REPO}"
    fi
else
    # Auto-resolve known FaradAiGuard upstream HF GGUF sources
    case "${MODEL_NAME}" in
        liquid-d1|d1)
            echo "  Auto-resolving Liquid AI d1-3B from Hugging Face..."
            TARGET_ARG="--hf-repo LiquidAI/d1-3B-GGUF --hf-file d1-3B-Q4_K_M.gguf"
            ;;
        pplx-decider|pplx-decider-flash)
            echo "  Auto-resolving Perplexity Decider Flash from Hugging Face..."
            TARGET_ARG="--hf-repo Jakevin/pplx-decider-flash-v1.2-GGUF --hf-file pplx-decider-flash-v1.2-Q4_K_M.gguf"
            ;;
        mica|mica-v0.5)
            echo "  Auto-resolving Mica v0.5-4B from Hugging Face..."
            TARGET_ARG="--hf-repo mradermacher/Mica-v0.5-4B-GGUF --hf-file Mica-v0.5-4B.Q4_K_M.gguf"
            ;;
        laya)
            echo "  Auto-resolving Laya-Guard from Hugging Face..."
            TARGET_ARG="--hf-repo ggml-org/Laya-GGUF --hf-file Laya-Q8_0.gguf"
            ;;
        granite)
            echo "  Auto-resolving Granite Guardian from Hugging Face..."
            TARGET_ARG="--hf-repo QuantFactory/granite-guardian-3.0-2b-GGUF --hf-file granite-guardian-3.0-2b.Q4_K_M.gguf"
            ;;
        qwen3guard)
            echo "  Auto-resolving Qwen3Guard from Hugging Face..."
            TARGET_ARG="--hf-repo Qwen/Qwen2.5-0.5B-Instruct-GGUF --hf-file qwen2.5-0.5b-instruct-q4_k_m.gguf"
            ;;
        *)
            echo "  Model file ${MODEL_FILE} not found; falling back to direct model path specification."
            TARGET_ARG="--model ${MODEL_FILE}"
            ;;
    esac
fi

GRAMMAR_ARG=""
if [ -f "/grammar/guard.gbnf" ]; then
    GRAMMAR_ARG="--grammar-file /grammar/guard.gbnf"
fi

echo "============================================="
echo "Executing: /app/llama-server --host ${HOST} --port ${PORT} ${TARGET_ARG} --ctx-size ${CTX_SIZE} ${GRAMMAR_ARG} --cont-batching --flash-attn ${FLASH_ATTN} $@"

exec /app/llama-server \
    --host "${HOST}" \
    --port "${PORT}" \
    ${TARGET_ARG} \
    --ctx-size "${CTX_SIZE}" \
    ${GRAMMAR_ARG} \
    --cont-batching \
    --flash-attn "${FLASH_ATTN}" \
    "$@"
