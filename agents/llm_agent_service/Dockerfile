
# FROM python:3.10-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi uvicorn transformers sentencepiece


# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]

# Use an official PyTorch image with CUDA (or CPU if not using GPU)
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8400

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8400"]

