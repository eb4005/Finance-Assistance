# # retriever_service/Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi uvicorn sentence-transformers faiss-cpu numpy

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.10-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
