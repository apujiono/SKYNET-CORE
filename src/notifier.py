import requests
import logging
from datetime import datetime

logger = logging.getLogger("Skynet")

def send_whatsapp_notification(threats, config, timestamp):
    try:
        message = f"⚠️ Peringatan Skynet {timestamp}:\n" + "\n".join([f"- {t['domain']}: Bahaya (Skor {t['score']:.0f}%)" for t in threats])
        requests.post("https://api.twilio.com/2010-04-01/Accounts/" + config["twilio_account_sid"] + "/Messages.json",
                     auth=(config["twilio_account_sid"], config["twilio_auth_token"]),
                     data={
                         "From": config["twilio_whatsapp_number"],
                         "To": config["whatsapp_number"],
                         "Body": message
                     })
        logger.info("WhatsApp notification sent.")
    except Exception as e:
        logger.error(f"WhatsApp notification error: {e}")