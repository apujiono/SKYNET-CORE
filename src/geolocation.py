import geoip2.database
import logging

logger = logging.getLogger("Skynet")

def get_domain_location(domain, config):
    """Dapatkan geolocation dari domain."""
    try:
        reader = geoip2.database.Reader("/app/data/GeoLite2-City.mmdb")
        response = requests.get(f"http://{domain}", timeout=5)
        ip = response.url.split("/")[2]
        geo = reader.city(ip)
        location = {"lat": geo.location.latitude, "lon": geo.location.longitude, "city": geo.city.name}
        logger.info(f"Geolocation for {domain}: {location}")
        return location
    except Exception as e:
        logger.error(f"Geolocation error for {domain}: {e}")
        return None