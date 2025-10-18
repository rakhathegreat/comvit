# ---------- compile ----------
FROM python:3.10.18-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# build-dep
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install -r requirements.txt

# ---------- runtime ----------
FROM python:3.10.18-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# runtime libs untuk opencv, mediapipe, sounddevice
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 \
        libxrender-dev libgomp1 libportaudio2 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv

WORKDIR /app
COPY ./app ./app

RUN useradd -m -u 1000 api && chown -R api:api /app
USER api

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]