# Unsubscribed Emails Tracker

[![Python Application Tests](https://github.com/onlymattjohnson/unsubscribe-email-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/onlymattjohnson/unsubscribe-email-tracker/actions/workflows/test.yml)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A personal browser extension + web app to track emails you unsubscribe from. This project includes a FastAPI backend, a PostgreSQL database, and a vanilla JavaScript browser extension.

## Core Features

#### API / Backend
-   FastAPI backend serving a secure REST API.
-   PostgreSQL database with Alembic for schema migrations.
-   Robust logging system with fallbacks to local files and Discord alerts.
-   Bearer Token authentication for the API.
-   Rate limiting to prevent abuse.

#### Web UI
-   A simple web interface served directly from the FastAPI app.
-   View, search, filter, and export your list of unsubscribed emails.
-   Protected by Basic Authentication.

#### Browser Extension
-   Manifest V3 extension for Chrome and Firefox.
-   Popup UI to submit unsubscribe data.
-   Automatically extracts sender information from open emails in Gmail.
-   Securely configured via an options page.

## Tech Stack

-   **Backend:** FastAPI, Uvicorn
-   **Database:** PostgreSQL, SQLAlchemy, Alembic
-   **Testing:** Pytest, Docker Compose
-   **Formatting:** Black
-   **Extension:** Vanilla JavaScript, HTML, CSS

---

## Getting Started: Local Development Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
-   Python 3.11+
-   PostgreSQL server running locally or in Docker.
-   An active Python virtual environment (recommended).

### 2. Initial Setup

1.  **Clone the repository:**
    ```bash
    git clone https://www.github.com/onlymattjohnson/unsubscribe-email-tracker.git
    cd unsub-tracker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    The project uses separate requirements files for production and development.
    ```bash
    # Install production and development dependencies
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

4.  **Set up the database:**
    You need two separate, empty PostgreSQL databases: one for development and one for testing.
    ```sql
    CREATE DATABASE unsub_tracker_db;
    CREATE DATABASE unsub_tracker_db_test;
    ```

5.  **Configure environment variables:**
    Copy the example `.env` file and fill in your details.
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file with your database URLs, a secure API token, and other required values.

6.  **Run database migrations:**
    Apply the schema to your **development** database.
    ```bash
    alembic upgrade head
    ```

7.  **Run the application:**
    ```bash
    make run
    ```
    The API will be available at `http://127.0.0.1:8000`.

---

## Running Tests and Quality Checks

This project uses a test harness to run all necessary checks from a single command.

### Running the Test Harness
Ensure your test database is running and your `.env` file is configured with `TEST_DATABASE_URL`.

To run all formatting checks, apply migrations to the test database, and run the full `pytest` suite with coverage, execute:
```bash
python scripts/test-harness.py
You can use flags to modify its behavior:

    --quick or --no-migrations: Skip the Alembic migration step.

    --no-format-check: Skip the black --check step.
```

### Test Coverage

The test harness enforces a minimum test coverage percentage (default is 80%). If coverage drops below this threshold, the check will fail.

A detailed, line-by-line HTML coverage report is generated at htmlcov/index.html after the test run.

## Browser Extension Development
Loading the Extension

You can load the extension directly from the extension/ directory for testing.

**Google Chrome**

1. Navigate to chrome://extensions.
2. Enable "Developer mode".
3. Click "Load unpacked" and select the extension folder.

**Mozilla Firefox**

1. Navigate to about:debugging.
2. Click "This Firefox", then "Load Temporary Add-on...".
3. Select the extension/manifest.json file.

## Manual Testing

A full checklist for manually testing the extension's UI and functionality is available at extension/MANUAL_TESTING_CHECKLIST.md.

## Continuous Integration (CI)

This repository uses GitHub Actions to automatically run all tests and quality checks on every push and pull request to the main branch. This ensures code quality and prevents regressions.

You can view the status of the CI runs in the "Actions" tab of the GitHub repository.

![alt text](https://github.com/onlymattjohnson/unsubscribe-email-tracker/actions/workflows/test.yml/badge.svg)