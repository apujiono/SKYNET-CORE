import argparse
from src.scanner import print_t800_logo
from src.database import init_quarantine_zone
from src.autopilot import Autopilot
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("Skynet")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("logs/skynet.log", maxBytes=2*1024*1024, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - T-800: %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    parser = argparse.ArgumentParser(description="Skynet 1000x - Cyber Security Framework")
    parser.add_argument("--min_terminators", type=int, default=10, help="Minimum T-800 agents")
    parser.add_argument("--interval", type=int, default=120, help="Scan interval in minutes")
    parser.add_argument("--monitor_interval", type=int, default=360, help="Monitor interval in minutes")
    args = parser.parse_args()

    config = {
        "scrape_url": "https://www.expireddomains.net/expired-domains/",
        "vt_api_key": "YOUR_VIRUSTOTAL_API_KEY",
        "maxmind_key": "YOUR_MAXMIND_KEY",
        "whois_api_key": "YOUR_WHOIS_API_KEY",
        "bert_model_path": "/app/data/bert_model",
        "resource_model_path": "/app/data/resource_model.pkl",
        "user_agents": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"],
        "proxies": {},
        "db_path": "/app/data/skynet_db.sqlite",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email_from": "your_email@gmail.com",
        "email_to": "recipient_email@gmail.com",
        "email_password": "your_app_specific_password",
        "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID",
        "discord_webhook": "YOUR_DISCORD_WEBHOOK",
        "slack_webhook": "YOUR_SLACK_WEBHOOK",
        "railway_api_token": "YOUR_RAILWAY_API_TOKEN",
        "railway_project_id": "YOUR_PROJECT_ID",
        "repo_url": "https://github.com/apujiono/SENTINEL-CORE.git",
        "dash_key": "skynet123",
        "hive_url": "https://your-skynet.up.railway.app"
    }

    setup_logging()
    print_t800_logo()
    init_quarantine_zone(config["db_path"])
    autopilot = Autopilot(config)
    autopilot.run()

if __name__ == "__main__":
    main()