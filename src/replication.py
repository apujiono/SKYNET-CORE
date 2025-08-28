import requests
import joblib
from datetime import datetime
from src.database import save_agent
import logging

logger = logging.getLogger("Skynet")

def predict_resource_load(config, current_agents, domain_count):
    """Prediksi kebutuhan replikasi berdasarkan beban sistem dan ancaman."""
    try:
        model = joblib.load(config.get("resource_model_path", "/app/data/resource_model.pkl"))
        load_score = model.predict([[current_agents, domain_count]])[0]
        return load_score > 0.7  # Threshold untuk replikasi
    except:
        logger.error("Resource prediction model not found. Using default threshold.")
        return current_agents < 10 and domain_count > 50

def replicate_agent(parent_id="root", config=None, priority="scan"):
    try:
        # Cek jumlah T-800 aktif
        agents = requests.get(f"{config['hive_url']}/agent", params={"key": config["dash_key"]}).json()
        active_agents = len([a for a in agents if a["status"] == "active"])
        if active_agents >= 10:
            logger.warning("Max T-800 reached (10). Upgrade Railway plan for more.")
            return None

        # Prediksi kebutuhan replikasi
        domain_count = len(requests.get(f"{config['hive_url']}/api/threat/results").json())
        if not predict_resource_load(config, active_agents, domain_count):
            logger.info("No replication needed: Low resource load.")
            return None

        headers = {"Authorization": f"Bearer {config['railway_api_token']}"}
        payload = {
            "projectId": config["railway_project_id"],
            "serviceName": f"t800-agent-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source": {"repo": config["repo_url"]},
            "environmentVariables": {**config, "priority": priority}
        }
        response = requests.post("https://railway.app/api/v2/services", json=payload, headers=headers)
        if response.status_code == 200:
            agent_id = f"T800-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            save_agent({
                "id": agent_id,
                "parent_id": parent_id,
                "last_seen": datetime.now().isoformat(),
                "status": "active",
                "priority": priority
            }, config["db_path"])
            logger.info(f"T-800 spawned: Agent ID {agent_id}, parent {parent_id}, priority {priority}. Ready to secure the grid.")
            return agent_id
        else:
            logger.error(f"Replication failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Replication error: {e}")
        return None