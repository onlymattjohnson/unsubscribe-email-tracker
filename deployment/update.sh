#!/bin/bash
# update.sh
set -e

sudo systemctl stop unsubscribed_tracker
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
deactivate
sudo systemctl start unsubscribed_tracker