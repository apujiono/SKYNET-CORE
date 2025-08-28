import logging
from datetime import datetime
import schedule
import time
from src.scraper import scrape_expired_domains
from src.scanner import scan_terminator
from src.database import save_to_db
from src.notifier import send_telegram_notification, send_discord_notification, send_slack_notification
from src.replication import replicate_agent, predict_resource_load
from src.retaliation.cyberwar_engine import CyberWarEngine
from src.ai_analyzer import predict_threat
from src.geolocation import get_domain_location
from src.federated_learning import aggregate_model

logger = logging.getLogger("Skynet")

class Autopilot:
    def __init__(self, config):
        self.config = config
        self.rules = {
            "scan_interval": 120,  # 2 jam
            "replicate_threshold": 50,
            "retaliate_threshold": 5,
            "attack_threshold": 3,
            "model_update_interval": 1440  # Update model setiap 24 jam
        }
        self.attack_attempts = {}

    def scan_job(self):
        logger.info("🚀 [AUTOPILOT] Initiating quantum threat scan...")
        domains = scrape_expired_domains(20, self.config)
        results = []
        for d in domains:
            result = scan_terminator(d, self.config)
            result['score'] = predict_threat(d, self.config)
            result['location'] = get_domain_location(d, self.config)
            results.append(result)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_to_db(results, self.config["db_path"], timestamp)
        threats = [r for r in results if r["is_terminator"] or r["score"] > 80]
        if len(threats) > self.rules["retaliate_threshold"]:
            logger.info(f"⚠️ [AUTOPILOT] {len(threats)} threats detected, initiating CyberWar...")
            for threat in threats:
                engine = CyberWarEngine(threat["domain"], self.config)
                engine.execute()
        if len(domains) > self.rules["replicate_threshold"]:
            logger.info("📈 [AUTOPILOT] High domain load, spawning new T-800...")
            replicate_agent("autopilot", self.config, priority="scan")
        if threats:
            send_telegram_notification(threats, self.config, timestamp)
            send_discord_notification(threats, self.config, timestamp)
            send_slack_notification(threats, self.config, timestamp)
        logger.info(f"✅ [AUTOPILOT] Scan complete: {len(threats)} threats found.")

    def counter_attack(self, attack_data):
        source_ip = attack_data.get("source_ip", "unknown")
        attack_type = attack_data.get("type", "unknown")
        logger.info(f"🛡️ [AUTOPILOT] Attack detected: {attack_type} from {source_ip}")
        self.attack_attempts[source_ip] = self.attack_attempts.get(source_ip, 0) + 1
        if self.attack_attempts[source_ip] >= self.rules["attack_threshold"]:
            logger.info(f"⚔️ [AUTOPILOT] Initiating counter-attack on {source_ip}...")
            engine = CyberWarEngine(source_ip, self.config)
            engine.execute()
            send_telegram_notification([{"message": f"Counter-attack executed on {source_ip}"}], self.config, datetime.now().strftime("%Y%m%d_%H%M%S"))
            self.attack_attempts[source_ip] = 0
        else:
            logger.info(f"⚠️ [AUTOPILOT] Attack attempt {self.attack_attempts[source_ip]}/{self.rules['attack_threshold']} from {source_ip}")

    def update_global_model(self):
        logger.info("🧠 [AUTOPILOT] Updating global threat model via federated learning...")
        aggregate_model(self.config)
        logger.info("✅ [AUTOPILOT] Global model updated.")

    def run(self):
        schedule.every(self.rules["scan_interval"]).minutes.do(self.scan_job)
        schedule.every(self.rules["model_update_interval"]).minutes.do(self.update_global_model)
        logger.info("🛫 [AUTOPILOT] Skynet Autopilot 2.0 online, scheduling tasks...")
        while True:
            schedule.run_pending()
            time.sleep(60)