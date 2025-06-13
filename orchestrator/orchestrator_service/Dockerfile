
# FROM python:3.10-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use an official Python image


# FROM python:3.10-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Create app directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements if you have one
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy app code
# COPY . .

# # Expose FastAPI port
# EXPOSE 8000

# # Run the FastAPI app with Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# FROM python:3.10-slim

# # Install netcat and healthcheck dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     netcat \
#     && rm -rf /var/lib/apt/lists/*

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Create app directory
# WORKDIR /app

# # Copy wait script
# COPY wait-for.sh ./wait-for.sh
# RUN chmod +x ./wait-for.sh

# # Copy requirements if you have one
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy app code
# COPY . .

# # Expose FastAPI port
# EXPOSE 8000

# # Add health check endpoint
# RUN echo "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}" > health.py

# # Run the wait script before starting
# CMD ["./wait-for.sh", "api-agent", "8001", "--", \
#      "./wait-for.sh", "retriever-agent", "8002", "--", \
#      "./wait-for.sh", "scraping-agent", "8003", "--", \
#      "./wait-for.sh", "llm-agent", "8400", "--", \
#      "./wait-for.sh", "voice-agent", "8000", "--", \
#      "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE $PORT

# Start the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]