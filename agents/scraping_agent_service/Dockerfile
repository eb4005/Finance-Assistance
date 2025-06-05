
# FROM python:3.10-slim

# WORKDIR /app

# COPY . .

# # RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir fastapi uvicorn feedparser


# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for pip and feedparser
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

