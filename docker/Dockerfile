# FaradAiGuard: Multi-Arch C++ Inference Container based on llama.cpp server
# Exposes OpenAI-compatible API on port 8088 with strict GBNF grammar enforcement
FROM ghcr.io/ggml-org/llama.cpp:server

ARG MODEL=qwen3guard
ARG GGUF_FILE=""

ENV MODEL_NAME=${MODEL}
ENV PORT=8088
ENV HOST=0.0.0.0
ENV CTX_SIZE=4096

WORKDIR /app

# Copy GBNF grammar
COPY grammar/guard.gbnf /grammar/guard.gbnf

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy model weights if baked into build context, or mount via volume
RUN mkdir -p /models
COPY models/ /models/

EXPOSE 8088

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8088/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
