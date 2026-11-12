# Development image for the EE271 SIMD simulator and its visualizer.
# Python matches the course environment (simd-part1/requirements.yml).
FROM python:3.13.5-slim

# `make` lets the course's own test Makefile run unchanged inside the container.
RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Run as an unprivileged user; the repo is bind-mounted at /work.
RUN useradd --create-home app
USER app
WORKDIR /work

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/work:/work/simd-part1
