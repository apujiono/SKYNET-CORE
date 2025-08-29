FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY templates/ templates/
COPY static/ static/
ENV DB_PATH=/app/data/skynet_db.sqlite
ENV MODEL_PATH=/app/src/data/model.pkl
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "120", "src.app:app"]