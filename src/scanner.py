import requests
import redis
import json
import time
import logging

logger = logging.getLogger("Skynet")

def scan_terminator(domain, config):
    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True, retry_on_timeout=True)
    cache_key = f"vt:{domain}"
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))
    
    result = {"domain": domain, "is_terminator": False, "details": {}}
    for attempt in range(3):
        try:
            response = requests.get(
                f"https://www.virustotal.com/api/v3/domains/{domain}",
                headers={"x-apikey": config["virustotal_api_key"]},
                timeout=5
            )
            if response.status_code == 200:
                result["is_terminator"] = response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0) > 0
                result["details"] = response.json()
                redis_client.setex(cache_key, 86400, json.dumps(result))
                logger.info(f"Scanned {domain}: {result['is_terminator']}")
                return result
            elif response.status_code == 429:
                logger.warning("VirusTotal rate limit hit, retrying in %s seconds...", 2 ** attempt)
                time.sleep(2 ** attempt)
            else:
                logger.error("VirusTotal error %s for %s", response.status_code, domain)
                break
        except Exception as e:
            logger.error("Scan error for %s: %s", domain, e)
            time.sleep(2 ** attempt)
    return result