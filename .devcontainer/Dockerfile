# Pinned to a Python 3.12 dev container base so the toolchain is reproducible.
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The core pipeline is offline by design. No Azure CLI, no database drivers, and no
# cloud credentials are installed here. Optional integrations document their own setup.
RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/fy27-database-modernization-factory
