import os
import requests
import logging

logger = logging.getLogger("Skynet")

def download_assets():
    geolite_path = os.getenv("GEOLITE_PATH")
    if not os.path.exists(geolite_path):
        url = "YOUR_GEOLITE2_URL"  # Ganti dengan link MaxMind GeoLite2
        try:
            with open(geolite_path, "wb") as f:
                f.write(requests.get(url, timeout=5).content)
            logger.info("GeoLite2 downloaded.")
        except Exception as e:
            logger.error(f"GeoLite2 download error: {e}")

if __name__ == "__main__":
    download_assets()