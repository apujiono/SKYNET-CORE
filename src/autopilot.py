import logging
from src.scanner import scan_terminator
from src.ai_analyzer import ThreatAnalyzer
from src.database import save_to_db
from src.notifier import send_whatsapp_notification
from datetime import datetime
import schedule
import time

logger = logging.getLogger("Skynet")

class Autopilot:
    def __init__(self, config):
        self.config = config
        self.analyzer = ThreatAnalyzer(config)
        self.rules = {
            "scan_interval": 3600,  # 1 jam
            "replicate_threshold": 50,
            "attack_threshold": 3
        }

    def scan_job(self):
        logger.info("🚀 [AUTOPILOT] Initiating threat scan...")
        domains = ["tokohpedia.xyz", "example.com"]  # Dummy domains untuk test
        results = []
        for d in domains[:10]:  # Batasi 10 domains/scan
            result = scan_terminator(d, self.config)
            result['score'] = self.analyzer.predict_threat(d)
            results.append(result)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_to_db(results, self.config["db_path"], timestamp)
        threats = [r for r in results if r["is_terminator"] or r['score'] > 80]
        if threats:
            send_whatsapp_notification(threats, self.config, timestamp)
        logger.info(f"✅ [AUTOPILOT] Scan complete: {len(threats)} threats found.")

    def run(self):
        schedule.every(self.rules["scan_interval"]).seconds.do(self.scan_job)
        while True:
            schedule.run_pending()
            time.sleep(60)