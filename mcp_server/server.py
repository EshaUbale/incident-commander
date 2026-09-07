import sqlite3
import os
import chromadb
from sentence_transformers import SentenceTransformer
from mcp.server.mcpserver import MCPServer
from datetime import datetime, timezone
mcp = MCPServer("incident-commander")

# RAG setup — loaded once at startup, reused for every search_runbooks call.
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "rag", "chroma_db")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
runbooks_collection = chroma_client.get_or_create_collection("runbooks")

# Points to the same file seed.py created.
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "incidents.db")


@mcp.tool()
def get_logs(service: str) -> str:
    """Get recent error logs for a given service name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timestamp, message, severity FROM logs WHERE service = ? ORDER BY timestamp DESC",
        (service,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No logs found for service '{service}'."

    lines = [f"{ts} [{sev}] {msg}" for ts, msg, sev in rows]
    return f"{len(rows)} log(s) found for '{service}':\n" + "\n".join(lines)


@mcp.tool()
def get_metrics(service: str) -> str:
    """Get recent CPU, error rate, and latency metrics for a given service name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timestamp, cpu_percent, error_rate, latency_ms FROM metrics WHERE service = ? ORDER BY timestamp DESC",
        (service,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No metrics found for service '{service}'."

    lines = [
        f"{ts} — CPU: {cpu}%, error rate: {err}%, latency: {lat}ms"
        for ts, cpu, err, lat in rows
    ]
    return f"{len(rows)} metric snapshot(s) found for '{service}':\n" + "\n".join(lines)

    
@mcp.tool()
def create_ticket(service: str, title: str, description: str, severity: str) -> str:
    """Create an incident ticket for a service. Use this after investigating, to log the issue for the team."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO tickets (service, title, description, severity, created_at) VALUES (?, ?, ?, ?, ?)",
        (service, title, description, severity, created_at),
    )
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()

    return f"Ticket #{ticket_id} created for '{service}': {title} (severity: {severity})"

 
@mcp.tool()
def search_runbooks(query: str) -> str:
    """Search historical incident runbooks for similar past issues. Use this before deep investigation, to check if this problem has happened before."""
    query_embedding = embedding_model.encode(query).tolist()

    results = runbooks_collection.query(
        query_embeddings=[query_embedding],
        n_results=2,
    )

    documents = results["documents"][0]
    filenames = results["metadatas"][0]

    if not documents:
        return "No matching runbooks found."

    output = []
    for doc, meta in zip(documents, filenames):
        output.append(f"--- {meta['filename']} ---\n{doc}")

    return "\n\n".join(output)

@mcp.tool()
def get_execution_trace(run_id: str) -> str:
    """Get the full execution trace for a given run, showing every agent action and tool call in order."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timestamp, agent_name, event_type, details FROM traces WHERE run_id = ? ORDER BY id ASC",
        (run_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No trace found for run_id '{run_id}'."

    lines = [f"[{ts}] {agent} — {etype}: {details}" for ts, agent, etype, details in rows]
    return f"Execution trace for run '{run_id}' ({len(rows)} events):\n" + "\n".join(lines)



if __name__ == "__main__":
    mcp.run()