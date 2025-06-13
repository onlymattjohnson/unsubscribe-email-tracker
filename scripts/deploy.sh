#!/bin/bash
set -e

echo ">>> Starting deployment..."

# 1. Pull the latest code from the main branch
echo "--- 1. Pulling latest code ---"
git pull origin main

# 2. Install/update dependencies
echo "--- 2. Installing dependencies ---"
# Assumes venv is in the parent directory of the script
source "$(dirname "$0")/../venv/bin/activate"
pip install -r "$(dirname "$0")/../requirements.txt"
deactivate

# 3. Run database migrations
echo "--- 3. Applying database migrations ---"
source "$(dirname "$0")/../venv/bin/activate"
alembic upgrade head
deactivate

# 4. Restart the application service
echo "--- 4. Restarting systemd service ---"
sudo systemctl restart unsubscribed_tracker

# 5. Health Check
echo "--- 5. Performing health check ---"
# Wait a few seconds for the service to start
sleep 5
# Curl the health check endpoint on the domain
# Replace with your actual domain
HEALTH_CHECK_URL="https://your_domain.com/api/v1/health"
STATUS_CODE=$(curl --silent --output /dev/stderr --write-out "%{http_code}" "$HEALTH_CHECK_URL")

if [ "$STATUS_CODE" -ne 200 ]; then
    echo "--- FAILED: Health check returned status $STATUS_CODE. Rolling back is not automated. Please check logs. ---"
    # A real rollback is complex. For now, we just alert.
    # sudo journalctl -u unsubscribed_tracker -n 50
    exit 1
else
    echo "--- SUCCESS: Health check passed with status 200. ---"
fi

echo ">>> Deployment finished successfully! <<<"