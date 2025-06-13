#!/bin/bash
set -e

# --- Configuration ---
# Load from .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

DB_NAME=$(echo $DATABASE_URL | awk -F/ '{print $NF}')
DB_USER=$(echo $DATABASE_URL | awk -F'[:/@]' '{print $4}')
BACKUP_DIR="/var/backups/unsubscribed_tracker"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=14 # Keep backups for 14 days


# --- Main Script ---
echo "--- Starting backup process at $(date) ---"

# 1. Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# 2. Perform database backup using pg_dump
echo "Backing up database '${DB_NAME}' to ${BACKUP_FILE}..."
PGPASSWORD=$DB_PASSWORD pg_dump -U "$DB_USER" -h localhost -d "$DB_NAME" | gzip > "$BACKUP_FILE"

# 3. Prune old backups
echo "Pruning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +${RETENTION_DAYS} -exec rm {} \;

echo "--- Backup process finished successfully. ---"