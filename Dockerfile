# syntax=docker/dockerfile:1

# PHES-ODM web validation tool.
#
#   docker build -t phes-odm-validation-web .
#   docker run --rm -p 3839:3839 phes-odm-validation-web
#
# Then open http://localhost:3839/

ARG PYTHON_VERSION=3.12


# ---------------------------------------------------------------- builder ----
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# git: requirements.txt pulls odm_sharing/odm_validation straight from GitHub
# build-essential: fallback for any dependency without a prebuilt wheel
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        git \
        build-essential \
 && rm -rf /var/lib/apt/lists/*

# Everything is installed into a venv so the runtime stage can copy one
# self-contained directory and leave the build toolchain behind.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install gunicorn


# ---------------------------------------------------------------- runtime ----
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=3839 \
    WEB_CONCURRENCY=2 \
    GUNICORN_THREADS=4 \
    GUNICORN_TIMEOUT=180

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY . /app

# Unprivileged runtime user. The app only writes to the background-callback
# diskcache under /tmp, so the source tree can stay read-only.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# src/app.py uses flat imports (`import stores`, `from components import ...`),
# so src/ has to be the working directory.
WORKDIR /app/src

EXPOSE 3839

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','3839')+'/', timeout=4)" || exit 1

# `server` is the Flask instance exported by src/app.py.
CMD ["sh", "-c", "exec gunicorn app:server \
      --bind 0.0.0.0:${PORT} \
      --workers ${WEB_CONCURRENCY} \
      --threads ${GUNICORN_THREADS} \
      --timeout ${GUNICORN_TIMEOUT} \
      --graceful-timeout 30 \
      --access-logfile - \
      --error-logfile -"]
