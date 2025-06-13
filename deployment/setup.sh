#!/bin/bash
set -e

# --- Configuration ---
# The user that the service will run as.
# Use 'whoami' to get the current user.
APP_USER=$(whoami)
# The absolute path to the project directory.
# This assumes the script is run from the project root.
PROJECT_PATH=$(readlink -f .)
VENV_PATH="$PROJECT_PATH/venv"
SERVICE_NAME="unsubscribed_tracker"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# --- Helper Functions ---
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Main Script ---
print_info "Starting Unsubscribed Tracker setup..."

# 1. Check System Requirements
print_info "Checking system requirements..."
command -v python3 >/dev/null 2>&1 || print_error "python3 is required but not installed."
command -v pip3 >/dev/null 2>&1 || print_error "pip3 is required but not installed."
command -v psql >/dev/null 2>&1 || print_error "psql (PostgreSQL client) is required. Please install postgresql-client."
print_success "System requirements met."

# 2. Check for .env file
if [ ! -f "$PROJECT_PATH/.env" ]; then
    print_error ".env file not found. Please copy .env.example to .env and configure it before running this script."
fi
print_success ".env file found."

# 3. Setup Python Virtual Environment
print_info "Setting up Python virtual environment at $VENV_PATH..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    print_success "Virtual environment created."
else
    print_info "Virtual environment already exists."
fi

# 4. Install Dependencies
print_info "Installing Python dependencies..."
source "$VENV_PATH/bin/activate"
pip install -r "$PROJECT_PATH/requirements.txt"
deactivate
print_success "Dependencies installed."

# 5a. Test database is running
print_info "Testing database connection..."
source "$VENV_PATH/bin/activate"
python3 -c "from app.database import engine; engine.connect().close()" || print_error "Failed to connect to database. Check your DATABASE_URL in .env"
deactivate

# 5b. Add rollback
print_info "Creating database backup..."
DB_NAME=$(grep DATABASE_URL .env | cut -d'/' -f4 | cut -d'?' -f1)
sudo -u postgres pg_dump $DB_NAME > "backup_$(date +%Y%m%d_%H%M%S).sql" 2>/dev/null || print_info "Skipping backup (may require postgres user permissions)"

# 5b. Run Database Migrations
print_info "Applying database migrations..."
source "$VENV_PATH/bin/activate"
alembic upgrade head
deactivate
print_success "Database migrations applied."

# 6. Create and Install systemd Service
print_info "Creating systemd service file..."
TEMPLATE_FILE="$PROJECT_PATH/deployment/unsubscribed_tracker.service.template"
CONFIGURED_SERVICE_FILE="/tmp/${SERVICE_NAME}.service"

# Replace placeholders in the template
sed -e "s|__USER__|${APP_USER}|g" \
    -e "s|__PROJECT_PATH__|${PROJECT_PATH}|g" \
    -e "s|__VENV_PATH__|${VENV_PATH}|g" \
    "$TEMPLATE_FILE" > "$CONFIGURED_SERVICE_FILE"

print_info "Installing systemd service to ${SERVICE_FILE}..."
# Use sudo to copy the file to the system directory
sudo cp "$CONFIGURED_SERVICE_FILE" "$SERVICE_FILE"
sudo chmod 644 "$SERVICE_FILE"

# 7. Reload systemd and Enable the Service
print_info "Reloading systemd daemon and enabling the service..."
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"

print_success "Setup complete!"
echo "--------------------------------------------------"
echo "The service '${SERVICE_NAME}' has been enabled and will start on the next reboot."
echo "To start the service immediately, run: sudo systemctl start ${SERVICE_NAME}"
echo "To check the status of the service, run: sudo systemctl status ${SERVICE_NAME}"
echo "To view the logs, run: sudo journalctl -u ${SERVICE_NAME} -f"
echo "--------------------------------------------------"