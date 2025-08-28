from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Response
import os
import json
import requests
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import redis
from src.database import init_quarantine_zone, save_alert, save_agent, save_command, get_zombie_results, get_alerts, get_agents, get_commands, save_to_db, save_model_params
from src.scraper import scrape_expired_domains
from src.scanner import scan_terminator, print_t800_logo
from src.notifier import send_email_notification, send_telegram_notification, send_discord_notification, send_slack_notification
from src.ai_analyzer import predict_threat
from src.geolocation import get_domain_location
from src.replication import replicate_agent
from src.retaliation.cyberwar_engine import CyberWarEngine
from src.autopilot import Autopilot
from src.federated_learning import aggregate_model

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'skynet-t800-omega')
app.permanent_session_lifetime = timedelta(minutes=30)

# Redis cache
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

# T-800 Logger
logger = logging.getLogger("Skynet")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/skynet.log", maxBytes=2*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - T-800: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Config
config = {
    "scrape_url": os.getenv("SCRAPE_URL", "https://www.expireddomains.net/expired-domains/"),
    "vt_api_key": os.getenv("VT_API_KEY"),
    "maxmind_key": os.getenv("MAXMIND_KEY"),
    "whois_api_key": os.getenv("WHOIS_API_KEY"),
    "bert_model_path": os.getenv("BERT_MODEL_PATH", "/app/data/bert_model"),
    "resource_model_path": os.getenv("RESOURCE_MODEL_PATH", "/app/data/resource_model.pkl"),
    "user_agents": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"],
    "proxies": {},
    "db_path": os.getenv("DB_PATH", "/app/data/skynet_db.sqlite"),
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "email_from": os.getenv("EMAIL_FROM"),
    "email_to": os.getenv("EMAIL_TO"),
    "email_password": os.getenv("EMAIL_PASSWORD"),
    "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
    "discord_webhook": os.getenv("DISCORD_WEBHOOK"),
    "slack_webhook": os.getenv("SLACK_WEBHOOK"),
    "railway_api_token": os.getenv("RAILWAY_API_TOKEN"),
    "railway_project_id": os.getenv("RAILWAY_PROJECT_ID"),
    "repo_url": os.getenv("REPO_URL", "https://github.com/apujiono/SENTINEL-CORE.git"),
    "dash_key": os.getenv("DASH_KEY", "skynet123"),
    "hive_url": os.getenv("HIVE_URL", "https://your-skynet.up.railway.app")
}

# Deadman switch
deadman_active = False
deadman_last_check = datetime.now()

# Autopilot
autopilot = Autopilot(config)

# 🔐 Login
def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            logger.warning(f"Intruder alert: Unauthorized access from {request.remote_addr}")
            save_alert({"message": f"Unauthorized access attempt from {request.remote_addr}"}, config["db_path"])
            autopilot.counter_attack({"type": "unauthorized_access", "source_ip": request.remote_addr})
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def check_auth():
    token = request.args.get('key') or (request.json.get('key') if request.is_json else None)
    if token == config["dash_key"]:
        logger.info("Access granted: Skynet Omega online.")
        return True
    logger.error(f"Access denied: Wrong key from {request.remote_addr}")
    save_alert({"message": f"Failed authentication from {request.remote_addr}"}, config["db_path"])
    autopilot.counter_attack({"type": "failed_auth", "source_ip": request.remote_addr})
    return False

# 🏠 Dashboard
@app.route('/')
@require_login
def dashboard():
    global deadman_active, deadman_last_check
    if deadman_active and (datetime.now() - deadman_last_check).total_seconds() > 24*3600:
        logger.info("Dead Man’s Switch triggered: Leaking intel to IPFS.")
        send_telegram_notification([{"message": "Skynet offline. Intel leaked."}], config, datetime.now().strftime("%Y%m%d_%H%M%S"))
        deadman_active = False
    alerts = get_alerts(config["db_path"])
    agents = get_agents(config["db_path"])
    threat_results = get_zombie_results(config["db_path"])
    return render_template('dashboard.html',
                          alerts=alerts,
                          agents=agents,
                          threat_results=threat_results,
                          deadman_active=deadman_active)

# 🚨 Terima alert
@app.route('/alert', methods=['POST'])
def receive_alert():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    data['time'] = datetime.now().strftime("%H:%M:%S")
    save_alert(data, config["db_path"])
    logger.info(f"Alert received: {data.get('message', 'Unknown')}")
    if any(keyword in data.get("message", "").lower() for keyword in ["attack", "phishing", "breach"]):
        autopilot.counter_attack({"type": "alert_triggered", "source_ip": data.get("source", request.remote_addr)})
    return jsonify({"status": "ok"})

# 🤖 Terima pendaftaran agent
@app.route('/agent', methods=['POST'])
def register_agent():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    data['last_seen'] = datetime.now().isoformat()
    data['parent_id'] = data.get('parent_id', None)
    data['status'] = 'active'
    data['priority'] = data.get('priority', 'scan')
    save_agent(data, config["db_path"])
    logger.info(f"T-800 Agent registered: {data.get('id', 'Unknown')} with priority {data['priority']}")
    return jsonify({"status": "registered"})

# 🧠 Terima parameter model dari T-800
@app.route('/agent/model', methods=['GET'])
def get_agent_model():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    agent_id = request.args.get('agent_id')
    # Dummy model params (ganti dengan model sebenarnya)
    return jsonify({"agent_id": agent_id, "params": [0.1, 0.2, 0.3]})

# 🧠 Update model T-800
@app.route('/agent/model/update', methods=['POST'])
def update_agent_model():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    logger.info(f"Model updated for T-800 {data['agent_id']}")
    return jsonify({"status": "updated"})

# 🧟 Threat Scanner
@app.route('/api/threat/scan', methods=['POST'])
@require_login
def api_scan_threat():
    keyword = request.json.get('keyword', 'phishing')
    cached = redis_client.get(f"scan:{keyword}")
    if cached:
        return jsonify(json.loads(cached))
    domains = scrape_expired_domains(20, config)
    results = []
    for d in domains:
        result = scan_terminator(d, config)
        result['score'] = predict_threat(d, config)
        result['location'] = get_domain_location(d, config)
        results.append(result)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_db(results, config["db_path"], timestamp)
    redis_client.setex(f"scan:{keyword}", 3600, json.dumps(results))
    threats = [r for r in results if r["is_terminator"] or r["score"] > 80]
    if len(domains) > config.get("replicate_threshold", 50):
        replicate_agent("root", config, priority="scan")
    if threats:
        send_email_notification(threats, config, timestamp)
        send_telegram_notification(threats, config, timestamp)
        send_discord_notification(threats, config, timestamp)
        send_slack_notification(threats, config, timestamp)
    logger.info(f"Quantum Threat Protocol: {len(threats)} threats acquired. Target locked.")
    return jsonify(results)

@app.route('/api/threat/results')
@require_login
def api_threat_results():
    results = get_zombie_results(config["db_path"])
    logger.info("Threat results retrieved for Skynet Omega dashboard.")
    return jsonify(results)

# 🤖 Kirim perintah ke agent
@app.route('/api/command', methods=['POST'])
@require_login
def api_command():
    data = request.json
    cmd = data.get('command')
    agent_id = data.get('agent_id')
    command = {
        "agent_id": agent_id,
        "command": cmd,
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }
    save_command(command, config["db_path"])
    logger.info(f"Command issued to T-800 {agent_id}: {cmd}. Target acquired.")
    return jsonify({"status": "command_sent", "agent": agent_id, "command": cmd})

# 🤖 Cek perintah untuk agent
@app.route('/agent/commands', methods=['GET'])
def get_agent_commands():
    agent_id = request.args.get('id')
    if not agent_id:
        logger.warning("No T-800 ID provided for command check.")
        return jsonify([])
    pending = get_commands(agent_id, config["db_path"])
    for cmd in pending:
        cmd['status'] = 'sent'
        save_command(cmd, config["db_path"])
    logger.info(f"Commands retrieved for T-800 {agent_id}: {len(pending)} pending.")
    return jsonify(pending)

# 🤖 Sinkronisasi antar T-800
@app.route('/agent/sync', methods=['POST'])
def sync_agents():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    agent_id = data.get('agent_id')
    shared_results = data.get('results', [])
    save_to_db(shared_results, config["db_path"], datetime.now().strftime("%Y%m%d_%H%M%S"))
    logger.info(f"T-800 {agent_id} synced {len(shared_results)} results.")
    return jsonify({"status": "synced"})

# ⚛️ Retaliation Engine (CyberWar)
@app.route('/api/retaliate', methods=['POST'])
@require_login
def api_retaliate():
    target = request.json.get('target')
    mode = request.json.get('mode', 'simulate')
    logger.info(f"Retaliation Engine: Targeting {target} with {mode} mode.")
    if mode == "cyberwar":
        engine = CyberWarEngine(target, config)
        engine.execute()
    else:
        save_alert({"message": f"Retaliation: {target} ({mode}) reported to registrar"}, config["db_path"])
        send_telegram_notification([{"message": f"Retaliation: {target} ({mode}) reported"}], config, datetime.now().strftime("%Y%m%d_%H%M%S"))
    return jsonify({"status": "reported", "target": target, "mode": mode})

# ⚰️ Dead Man's Switch
@app.route('/api/deadman/activate', methods=['POST'])
@require_login
def api_deadman_activate():
    global deadman_active, deadman_last_check
    deadman_active = True
    deadman_last_check = datetime.now()
    logger.info("Dead Man’s Switch activated. Skynet will leak intel if offline.")
    send_telegram_notification([{"message": "Dead Man’s Switch activated"}], config, datetime.now().strftime("%Y%m%d_%H%M%S"))
    return jsonify({"status": "activated"})

# 📊 Analytics
@app.route('/api/analytics')
@require_login
def api_analytics():
    results = get_zombie_results(config["db_path"])
    stats = {
        "total_domains": len(results),
        "threats": len([r for r in results if r["is_terminator"] or r["score"] > 80]),
        "malicious": len([r for r in results if r["malicious"]])
    }
    return jsonify(stats)

# 📥 Export Results
@app.route('/api/export/<format>')
@require_login
def api_export(format):
    results = get_zombie_results(config["db_path"])
    if format == "csv":
        output = "domain,is_terminator,malicious,score\n" + "\n".join(
            f"{r['domain']},{r['is_terminator']},{r['malicious']},{r.get('score', 0)}" for r in results
        )
        return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=threats.csv"})
    return jsonify(results)

# 📜 Evidence Endpoint
@app.route('/evidence', methods=['POST'])
def receive_evidence():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    save_alert({"message": f"CyberWar evidence: {data['target']} neutralized", "evidence": data}, config["db_path"])
    logger.info(f"CyberWar evidence received for {data['target']}")
    return jsonify({"status": "received"})

# 🚨 Attack Detection
@app.route('/api/attack', methods=['POST'])
def detect_attack():
    if not check_auth():
        return "🔐 Target denied: Unauthorized.", 403
    data = request.json
    logger.info(f"⚠️ [ATTACK] Detected: {data.get('type', 'unknown')} from {data.get('source_ip', 'unknown')}")
    autopilot.counter_attack(data)
    return jsonify({"status": "counter_attack_initiated"})

# 🤖 Replikasi T-800
@app.route('/api/replicate', methods=['POST'])
@require_login
def api_replicate():
    parent_id = request.json.get('parent_id', 'root')
    priority = request.json.get('priority', 'scan')
    agent_id = replicate_agent(parent_id, config, priority)
    if agent_id:
        return jsonify({"status": "replicated", "agent_id": agent_id, "priority": priority})
    return jsonify({"status": "failed"}), 500

# 🚪 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == config["dash_key"]:
            session['logged_in'] = True
            session.permanent = True
            logger.info("Access granted: Skynet Omega online.")
            return redirect('/')
        else:
            logger.error(f"Intruder alert: Wrong password from {request.remote_addr}")
            save_alert({"message": f"Failed login from {request.remote_addr}"}, config["db_path"])
            autopilot.counter_attack({"type": "failed_login", "source_ip": request.remote_addr})
            return "❌ Password salah", 403
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    logger.info("Session terminated. Hasta la vista.")
    return redirect('/login')

if __name__ == '__main__':
    print_t800_logo()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)