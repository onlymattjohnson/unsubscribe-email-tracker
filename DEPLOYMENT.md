# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Unsubscribed Tracker application to a production Linux server (e.g., Ubuntu 22.04 on DigitalOcean).

## 1. Prerequisites

- A registered domain name (e.g., `your_domain.com`).
- A fresh Linux server instance (Ubuntu 22.04 recommended).
- SSH access to the server with a non-root user that has `sudo` privileges.
- A production PostgreSQL database (either on the same server or a managed service).

## 2. Initial Server Setup

1.  **SSH into your server.**
2.  **Update system packages:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
3.  **Install required software:**
    ```bash
    sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git
    ```

## 3. Application Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
    cd <YOUR_REPO>
    ```

2.  **Run the setup script:** This will create the venv, install dependencies, and set up the systemd service.
    ```bash
    chmod +x deployment/setup.sh
    ./deployment/setup.sh
    ```
    *Note: The script requires `sudo` for the systemd steps and will prompt for your password.*

## 4. Database Setup

1.  **Create Production Database and User:**
    Log in to PostgreSQL and create a dedicated user and database for the production application.
    ```sql
    CREATE DATABASE unsub_tracker_prod_db;
    CREATE USER prod_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE unsub_tracker_prod_db TO prod_user;
    ```

2.  **Configure Environment Variables:**
    Copy the production environment template and fill in your details.
    ```bash
    cp deployment/env.production.example .env
    nano .env
    ```
    Fill in `DATABASE_URL`, `API_TOKEN`, and other variables.

3.  **Apply Migrations:**
    Run the deploy script to apply migrations to the production database.
    ```bash
    chmod +x scripts/deploy.sh
    ./scripts/deploy.sh
    ```

## 5. Nginx and SSL Setup

1.  **Configure Nginx:**
    Copy the provided Nginx config and enable it.
    ```bash
    sudo cp deployment/nginx/unsubscribed-tracker.conf /etc/nginx/sites-available/
    sudo nano /etc/nginx/sites-available/unsubscribed-tracker.conf # Replace your_domain.com
    sudo ln -s /etc/nginx/sites-available/unsubscribed-tracker.conf /etc/nginx/sites-enabled/
    sudo nginx -t # Test configuration
    ```

2.  **Obtain SSL Certificate with Certbot:**
    Certbot will automatically obtain a free SSL certificate from Let's Encrypt and configure Nginx to use it.
    ```bash
    sudo certbot --nginx -d your_domain.com
    ```
    Follow the on-screen prompts.

3.  **Restart Nginx:**
    ```bash
    sudo systemctl restart nginx
    ```

## 6. Service Management

The application runs as a `systemd` service called `unsubscribed_tracker`.

- **Start the service:** `sudo systemctl start unsubscribed_tracker`
- **Stop the service:** `sudo systemctl stop unsubscribed_tracker`
- **Restart the service:** `sudo systemctl restart unsubscribed_tracker`
- **Check status:** `sudo systemctl status unsubscribed_tracker`
- **View logs:** `sudo journalctl -u unsubscribed_tracker -f`

## 7. Backup and Monitoring

- **Backups:** A backup script is provided at `scripts/backup.sh`. It's recommended to run this script daily via a cron job.
  ```bash
  # Example cron job to run daily at 3 AM
  0 3 * * * /path/to/your/project/scripts/backup.sh
  ```
