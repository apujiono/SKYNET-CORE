import logging
from src.database import save_agent
from datetime import datetime

logger = logging.getLogger("Skynet")

def replicate_agent(parent_id="root", config=None, priority="scan"):
    agent_id = f"T800-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        save_agent({
            "id": agent_id,
            "parent_id": parent_id,
            "last_seen": datetime.now().isoformat(),
            "status": "active",
            "priority": priority
        }, config["db_path"])
        logger.info(f"T-800 spawned: {agent_id}")
        return agent_id
    except Exception as e:
        logger.error(f"Replication error: {e}")
        return None