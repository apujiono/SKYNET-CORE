FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY templates/ templates/
COPY static/ static/
ENV DB_PATH=/app/data/skynet_db.sqlite
ENV GEOLITE_PATH=/app/data/GeoLite2-City.mmdb
ENV MODEL_PATH=/app/src/data/model.pkl
CMD ["bash", "-c", "mkdir -p /app/data && python src/download_assets.py && gunicorn -w 1 -b 0.0.0.0:8080 src.app:app"]