# # exposure_service/Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi uvicorn yfinance pandas

# # Create directory structure for portfolio
# RUN mkdir -p ../../data_ingestion
# COPY portfolio.csv ../../data_ingestion/portfolio.csv

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pandas yfinance


# RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
