# # news_service/Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi uvicorn feedparser beautifulsoup4

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.10-slim

WORKDIR /app

COPY . .

# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn feedparser


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
