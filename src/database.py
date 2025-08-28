import sqlite3
import json
import logging

logger = logging.getLogger("Skynet")

def init_quarantine_zone(db_path):
    """Inisialisasi database SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            data TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            data TEXT,
            time TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            parent_id TEXT,
            last_seen TEXT,
            status TEXT,
            priority TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            command TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            params TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Quarantine Zone initialized.")

def save_to_db(results, db_path, timestamp):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for result in results:
        cursor.execute("INSERT INTO threats (domain, data, timestamp) VALUES (?, ?, ?)",
                      (result["domain"], json.dumps(result), timestamp))
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(results)} threats to database.")

def save_alert(data, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alerts (message, data, time) VALUES (?, ?, ?)",
                  (data.get("message", ""), json.dumps(data), data.get("time", "")))
    conn.commit()
    conn.close()

def save_agent(data, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agents (data, parent_id, last_seen, status, priority) VALUES (?, ?, ?, ?, ?)",
                  (json.dumps(data), data.get("parent_id"), data.get("last_seen"), data.get("status"), data.get("priority", "scan")))
    conn.commit()
    conn.close()

def save_command(data, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO commands (agent_id, command, status, timestamp) VALUES (?, ?, ?, ?)",
                  (data["agent_id"], data["command"], data["status"], data["timestamp"]))
    conn.commit()
    conn.close()

def save_model_params(data, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO model_params (params, timestamp) VALUES (?, ?)",
                  (json.dumps(data["params"]), data.get("timestamp", "")))
    conn.commit()
    conn.close()

def get_zombie_results(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM threats")
    results = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.close()
    return results

def get_alerts(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT message, data, time FROM alerts ORDER BY time DESC LIMIT 50")
    alerts = [{"message": row[0], "data": json.loads(row[1]), "time": row[2]} for row in cursor.fetchall()]
    conn.close()
    return alerts

def get_agents(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT data, parent_id, last_seen, status, priority FROM agents")
    agents = [{"data": json.loads(row[0]), "parent_id": row[1], "last_seen": row[2], "status": row[3], "priority": row[4]} for row in cursor.fetchall()]
    conn.close()
    return agents

def get_commands(agent_id, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT agent_id, command, status, timestamp FROM commands WHERE agent_id = ? AND status = 'pending'", (agent_id,))
    commands = [{"agent_id": row[0], "command": row[1], "status": row[2], "timestamp": row[3]} for row in cursor.fetchall()]
    conn.close()
    return commands