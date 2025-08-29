FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
# Install build dependencies untuk mengompilasi dari source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --no-binary numpy,scikit-learn -r requirements.txt
COPY src/ src/
COPY templates/ templates/
COPY static/ static/
ENV DB_PATH=/app/data/skynet_db.sqlite
ENV MODEL_PATH=/app/src/data/model.pkl
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "120", "src.app:app"]