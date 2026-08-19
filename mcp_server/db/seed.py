import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "incidents.db")


def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            cpu_percent REAL NOT NULL,
            error_rate REAL NOT NULL,
            latency_ms INTEGER NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)


def seed_logs(conn):
    fake_logs = [
        ("checkout", "2026-08-16 14:32:01", "Connection timeout to payment-gateway", "error"),
        ("checkout", "2026-08-16 14:33:10", "Retry failed after 3 attempts", "error"),
        ("checkout", "2026-08-16 14:34:02", "Circuit breaker opened for payment-gateway", "critical"),
        ("auth", "2026-08-16 09:12:44", "JWT validation failed: expired token", "warning"),
        ("auth", "2026-08-15 22:01:15", "Rate limit exceeded for login endpoint", "warning"),
        ("inventory", "2026-08-14 03:45:00", "Database connection pool exhausted", "critical"),
        ("inventory", "2026-08-14 03:46:12", "Failed to sync stock levels", "error"),
    ]

    conn.executemany(
        "INSERT INTO logs (service, timestamp, message, severity) VALUES (?, ?, ?, ?)",
        fake_logs,
    )


def seed_metrics(conn):
    fake_metrics = [
        ("checkout", "2026-08-16 14:30:00", 45.2, 0.8, 120),
        ("checkout", "2026-08-16 14:32:00", 78.5, 12.4, 890),
        ("checkout", "2026-08-16 14:34:00", 91.3, 34.1, 2100),
        ("auth", "2026-08-16 09:10:00", 22.1, 1.2, 95),
        ("auth", "2026-08-16 09:12:00", 25.4, 3.5, 140),
        ("inventory", "2026-08-14 03:44:00", 88.9, 5.6, 310),
        ("inventory", "2026-08-14 03:46:00", 95.2, 18.9, 780),
    ]

    conn.executemany(
        "INSERT INTO metrics (service, timestamp, cpu_percent, error_rate, latency_ms) VALUES (?, ?, ?, ?, ?)",
        fake_metrics,
    )


def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_logs(conn)
    seed_metrics(conn)
    conn.commit()
    conn.close()
    print(f"Seeded database at {DB_PATH}")


if __name__ == "__main__":
    main()