# # llm_agent_service/Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi uvicorn transformers torch accelerate sentencepiece

# # Enable GPU support if available
# ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX"

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.10-slim

WORKDIR /app

COPY . .

# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn transformers sentencepiece


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
