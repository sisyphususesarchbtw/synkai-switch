FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends git python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @openai/codex@0.160.0
RUN mkdir -p /home/node/.codex /workspace && chown -R node:node /home/node/.codex /workspace
USER node
WORKDIR /workspace
ENV CODEX_HOME=/home/node/.codex
ENTRYPOINT ["codex"]
