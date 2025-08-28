import smtplib
import requests
from email.mime.text import MIMEText
import logging

logger = logging.getLogger("Skynet")

def send_email_notification(threats, config, timestamp):
    try:
        msg = MIMEText(f"Skynet Threat Report {timestamp}:\n\n" + "\n".join([f"{t['domain']}: Score {t['score']:.2f}" for t in threats]))
        msg["Subject"] = f"Skynet Threat Report {timestamp}"
        msg["From"] = config["email_from"]
        msg["To"] = config["email_to"]
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["email_from"], config["email_password"])
            server.send_message(msg)
        logger.info("Email notification sent.")
    except Exception as e:
        logger.error(f"Email notification error: {e}")

def send_telegram_notification(threats, config, timestamp):
    try:
        message = f"Skynet Threat Report {timestamp}:\n" + "\n".join([f"{t['domain']}: Score {t['score']:.2f}" for t in threats])
        requests.post(f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage",
                     data={"chat_id": config["telegram_chat_id"], "text": message})
        logger.info("Telegram notification sent.")
    except Exception as e:
        logger.error(f"Telegram notification error: {e}")

def send_discord_notification(threats, config, timestamp):
    try:
        message = f"Skynet Threat Report {timestamp}:\n" + "\n".join([f"{t['domain']}: Score {t['score']:.2f}" for t in threats])
        requests.post(config["discord_webhook"], json={"content": message})
        logger.info("Discord notification sent.")
    except Exception as e:
        logger.error(f"Discord notification error: {e}")

def send_slack_notification(threats, config, timestamp):
    try:
        message = f"Skynet Threat Report {timestamp}:\n" + "\n".join([f"{t['domain']}: Score {t['score']:.2f}" for t in threats])
        requests.post(config["slack_webhook"], json={"text": message})
        logger.info("Slack notification sent.")
    except Exception as e:
        logger.error(f"Slack notification error: {e}")