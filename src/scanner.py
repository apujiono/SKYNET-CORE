import requests
import whois
import dns.resolver
import logging

logger = logging.getLogger("Skynet")

def print_t800_logo():
    print("""
    ████████╗ ██████╗  ██████╗ ██████╗ 
    ╚══██╔══╝██╔═══██╗██╔═══██╗██╔══██╗
       ██║   ██║   ██║██║   ██║██████╔╝
       ██║   ██║   ██║██║   ██║██╔═══╝ 
       ██║   ╚██████╔╝╚██████╔╝██║     
       ╚═╝    ╚═════╝  ╚═════╝ ╚═╝     
    Skynet 1000x - Hasta la vista, threats!
    """)

def scan_terminator(domain, config):
    """Scan domain untuk deteksi ancaman."""
    try:
        whois_data = whois.whois(domain)
        vt_url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {"x-apikey": config["vt_api_key"]}
        vt_response = requests.get(vt_url, headers=headers, timeout=5)
        vt_data = vt_response.json() if vt_response.status_code == 200 else {}
        dns_records = dns.resolver.resolve(domain, "A", raise_on_no_answer=False)
        result = {
            "domain": domain,
            "is_terminator": vt_data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0) > 0,
            "malicious": vt_data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0),
            "whois": {"registrar": whois_data.get("registrar", "Unknown"), "created": str(whois_data.get("creation_date", ""))},
            "dns": [str(r) for r in dns_records]
        }
        logger.info(f"Scanned {domain}: {'Threat' if result['is_terminator'] else 'Safe'}")
        return result
    except Exception as e:
        logger.error(f"Scan error for {domain}: {e}")
        return {"domain": domain, "is_terminator": False, "malicious": 0, "whois": {}, "dns": []}