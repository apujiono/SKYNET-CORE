import requests
import logging

logger = logging.getLogger("Skynet")

def sync_gossip(agent_id, results, config):
    """Sinkronisasi data antar T-800 via gossip protocol."""
    try:
        agents = requests.get(f"{config['hive_url']}/agent", params={"key": config["dash_key"]}).json()
        active_agents = [a["data"]["id"] for a in agents if a["status"] == "active" and a["data"]["id"] != agent_id]
        for target_agent in active_agents[:2]:  # Batasi ke 2 agent untuk efisiensi
            response = requests.post(f"{config['hive_url']}/agent/sync", 
                                  json={"agent_id": agent_id, "results": results, "key": config["dash_key"]},
                                  timeout=5)
            if response.status_code == 200:
                logger.info(f"T-800 {agent_id} synced with {target_agent}")
    except Exception as e:
        logger.error(f"Gossip sync error for {agent_id}: {e}")