import sqlite3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("Skynet")

def save_to_db(results, db_path, timestamp):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT,
                score REAL,
                is_terminator BOOLEAN,
                timestamp TEXT,
                details TEXT
            )
        """)
        for result in results:
            cursor.execute(
                "INSERT INTO threats (domain, score, is_terminator, timestamp, details) VALUES (?, ?, ?, ?, ?)",
                (result["domain"], result["score"], result["is_terminator"], timestamp, str(result["details"]))
            )
        cursor.execute("DELETE FROM threats WHERE timestamp < ?", 
                      ((datetime.now() - timedelta(days=7)).strftime("%Y%m%d_%H%M%S"),))
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(results)} results to database.")
    except Exception as e:
        logger.error(f"Database error: {e}")

def save_agent(agent, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                parent_id TEXT,
                last_seen TEXT,
                status TEXT,
                priority TEXT
            )
        """)
        cursor.execute(
            "INSERT OR REPLACE INTO agents (id, parent_id, last_seen, status, priority) VALUES (?, ?, ?, ?, ?)",
            (agent["id"], agent["parent_id"], agent["last_seen"], agent["status"], agent["priority"])
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved agent {agent['id']} to database.")
    except Exception as e:
        logger.error(f"Agent save error: {e}")

def get_zombie_results(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM threats WHERE timestamp > ?", 
                      ((datetime.now() - timedelta(days=1)).strftime("%Y%m%d_%H%M%S"),))
        results = [{"domain": r[1], "score": r[2], "is_terminator": bool(r[3]), "timestamp": r[4], "details": r[5]} 
                   for r in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Database read error: {e}")
        return []