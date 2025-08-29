import logging
from src.autopilot import Autopilot
from src.database import save_agent
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, filename="/app/data/skynet.log", maxBytes=1000000, backupCount=1)
logger = logging.getLogger("Skynet")

def main(config):
    logger.info("🚀 Skynet Omega initializing...")
    save_agent({
        "id": "T800-root",
        "parent_id": None,
        "last_seen": datetime.now().isoformat(),
        "status": "active",
        "priority": "root"
    }, config["db_path"])
    config["min_terminators"] = 2
    autopilot = Autopilot(config)
    autopilot.run()

if __name__ == "__main__":
    config = {
        "db_path": os.getenv("DB_PATH", "/app/data/skynet_db.sqlite"),
        "model_path": os.getenv("MODEL_PATH", "/app/src/data/model.pkl"),
        "virustotal_api_key": os.getenv("VIRUSTOTAL_API_KEY"),
        "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
        "twilio_auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
        "twilio_whatsapp_number": os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"),
        "whatsapp_number": os.getenv("WHATSAPP_NUMBER", "whatsapp:+6281234567890"),
        "min_terminators": 2,
        "scan_interval": 3600,
        "monitor_interval": 3600
    }
    main(config)