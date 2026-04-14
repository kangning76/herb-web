"""Wait for the database to accept connections before proceeding."""
import socket
import sys
import time
from urllib.parse import urlparse

from app.config import settings

MAX_RETRIES = 30
RETRY_INTERVAL = 2

parsed = urlparse(settings.DATABASE_URL.replace("+asyncpg", ""))
host = parsed.hostname or "localhost"
port = parsed.port or 5432

print(f"Waiting for database at {host}:{port}...")
for i in range(1, MAX_RETRIES + 1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        print("Database is accepting connections.")
        sys.exit(0)
    except (socket.error, OSError):
        print(f"  DB not ready, retrying in {RETRY_INTERVAL}s... ({i}/{MAX_RETRIES})")
        time.sleep(RETRY_INTERVAL)

print("ERROR: Could not connect to database, giving up.")
sys.exit(1)
