import requests
import logging
import numpy as np
from src.database import save_model_params

logger = logging.getLogger("Skynet")

def aggregate_model(config):
    """Agregasi parameter model dari semua T-800 untuk update global model."""
    try:
        agents = requests.get(f"{config['hive_url']}/agent", params={"key": config["dash_key"]}).json()
        model_params = []
        for agent in agents:
            if agent["status"] == "active":
                response = requests.get(f"{config['hive_url']}/agent/model", params={"agent_id": agent["data"]["id"], "key": config["dash_key"]})
                if response.status_code == 200:
                    model_params.append(response.json()["params"])
        if not model_params:
            logger.warning("No model parameters received from T-800 agents.")
            return
        # Agregasi sederhana: rata-rata parameter
        global_params = np.mean(model_params, axis=0).tolist()
        save_model_params({"params": global_params, "timestamp": datetime.now().isoformat()}, config["db_path"])
        logger.info("Global model parameters updated and saved.")
        # Broadcast ke semua T-800
        for agent in agents:
            if agent["status"] == "active":
                requests.post(f"{config['hive_url']}/agent/model/update", 
                             json={"agent_id": agent["data"]["id"], "params": global_params, "key": config["dash_key"]},
                             timeout=5)
    except Exception as e:
        logger.error(f"Federated learning error: {e}")