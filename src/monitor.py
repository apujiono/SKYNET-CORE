import requests
import logging
from datetime import datetime

logger = logging.getLogger("Skynet")

def monitor_domain(domain, config):
    """Pantau perubahan pada domain."""
    try:
        response = requests.get(f"http://{domain}", timeout=5)
        status = "active" if response.status_code == 200 else "inactive"
        logger.info(f"Monitoring {domain}: Status {status}")
        return {"domain": domain, "status": status, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Monitoring error for {domain}: {e}")
        return {"domain": domain, "status": "unreachable", "timestamp": datetime.now().isoformat()}