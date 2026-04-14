#!/bin/sh
set -e

python -m app.wait_for_db
python -m app.seed_admin
python -m app.seed_herbs
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
