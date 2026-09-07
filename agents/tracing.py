import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "db", "incidents.db")


def log_event(run_id, agent_name, event_type, details):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO traces (run_id, timestamp, agent_name, event_type, details) VALUES (?, ?, ?, ?, ?)",
        (run_id, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), agent_name, event_type, details),
    )
    conn.commit()
    conn.close()