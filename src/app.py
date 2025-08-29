from flask import Flask, jsonify, request, render_template
from src.database import get_zombie_results, save_to_db
from src.scanner import scan_terminator
from src.ai_analyzer import ThreatAnalyzer
from src.notifier import send_whatsapp_notification
from src.replication import replicate_agent
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename="/app/data/skynet.log", maxBytes=1000000, backupCount=1)
logger = logging.getLogger("Skynet")
config = {
    "db_path": os.getenv("DB_PATH", "/app/data/skynet_db.sqlite"),
    "model_path": os.getenv("MODEL_PATH", "/app/src/data/model.pkl"),
    "geolite_path": os.getenv("GEOLITE_PATH", "/app/data/GeoLite2-City.mmdb"),
    "virustotal_api_key": os.getenv("VIRUSTOTAL_API_KEY"),
    "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
    "twilio_auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
    "twilio_whatsapp_number": os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"),
    "whatsapp_number": os.getenv("WHATSAPP_NUMBER", "whatsapp:+6281234567890")
}
analyzer = ThreatAnalyzer(config)

def check_auth():
    return request.args.get("key") == "skynet123"

@app.route('/')
def index():
    return render_template('dashboard.html', alerts=[])

@app.route('/api/threat/scan', methods=['POST'])
def scan_threat():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    keyword = request.json.get('keyword')
    result = scan_terminator(keyword, config)
    result['score'] = analyzer.predict_threat(keyword)
    save_to_db([result], config["db_path"], datetime.now().strftime("%Y%m%d_%H%M%S"))
    if result["is_terminator"] or result["score"] > 80:
        send_whatsapp_notification([result], config, datetime.now().strftime("%Y%m%d_%H%M%S"))
    return jsonify(result)

@app.route('/api/threat/results')
def threat_results():
    results = get_zombie_results(config["db_path"])
    return jsonify(results)

@app.route('/api/replicate', methods=['POST'])
def replicate():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    agent_id = replicate_agent(data.get("parent_id", "root"), config, data.get("priority", "scan"))
    return jsonify({"status": "replicated", "agent_id": agent_id})

@app.route('/api/whatsapp', methods=['POST'])
def whatsapp_bot():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    message = data.get('Body', '').lower()
    from_number = data.get('From', '')
    response = {"status": "ok", "message": ""}
    
    if message.startswith("scan "):
        link = message[5:].strip()
        result = scan_terminator(link, config)
        result['score'] = analyzer.predict_threat(link)
        save_to_db([result], config["db_path"], datetime.now().strftime("%Y%m%d_%H%M%S"))
        if result["is_terminator"] or result["score"] > 80:
            response["message"] = f"⚠️ {link}: Bahaya (Skor {result['score']:.0f}%)! Jangan klik!"
            send_whatsapp_notification([result], config, datetime.now().strftime("%Y%m%d_%H%M%S"))
        else:
            response["message"] = f"✅ {link}: Aman (Skor {result['score']:.0f}%)."
    
    elif message == "tambah t-800":
        agent_id = replicate_agent("whatsapp", config, priority="scan")
        response["message"] = f"T-800 baru aktif: {agent_id}" if agent_id else "Gagal menambah T-800."
    
    elif message == "status":
        results = get_zombie_results(config["db_path"])
        threats = len([r for r in results if r["is_terminator"] or r["score"] > 80])
        response["message"] = f"Status Skynet: {threats} ancaman ditemukan hari ini."
    
    requests.post("https://api.twilio.com/2010-04-01/Accounts/YOUR_TWILIO_SID/Messages.json",
                 auth=(config["twilio_account_sid"], config["twilio_auth_token"]),
                 data={"From": config["twilio_whatsapp_number"], "To": from_number, "Body": response["message"]})
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)