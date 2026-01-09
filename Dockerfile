# Multi-stage build for Qwen3-VL Inference Server

# Stage 1: Base image with CUDA support
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    vim \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# Stage 2: Builder stage for dependencies
FROM base as builder

# Set working directory
WORKDIR /tmp

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 3: Final runtime image
FROM base

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash qwen && \
    mkdir -p /app /models /cache && \
    chown -R qwen:qwen /app /models /cache

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=qwen:qwen /root/.local /home/qwen/.local

# Copy application code
COPY --chown=qwen:qwen app/ ./app/
COPY --chown=qwen:qwen main.py .
COPY --chown=qwen:qwen requirements.txt .

# Set Python path to include user site-packages
ENV PATH=/home/qwen/.local/bin:$PATH \
    PYTHONPATH=/app:$PYTHONPATH \
    HF_HOME=/cache/huggingface \
    TRANSFORMERS_CACHE=/cache/transformers \
    VLLM_WORKER_MULTIPROC_METHOD=spawn

# Create cache directories
RUN mkdir -p /cache/huggingface /cache/transformers && \
    chown -R qwen:qwen /cache

# Switch to non-root user
USER qwen

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python3", "main.py"]
