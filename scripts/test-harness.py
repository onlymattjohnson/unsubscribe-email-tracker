#!/usr/bin/env python3
"""
Test harness script that runs code quality checks and tests.
Usage: python scripts/test_harness.py [--quick] [--no-migrations]
"""
import subprocess
import sys
import os
import time
import argparse
from pathlib import Path

# ANSI color codes for better visibility
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(message):
    """Print a formatted header message."""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{message:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")


def print_success(message):
    """Print a success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print an error message in red."""
    print(f"{RED}✗ {message}{RESET}")


def print_warning(message):
    """Print a warning message in yellow."""
    print(f"{YELLOW}⚠ {message}{RESET}")


def run_command(command, env=None, description=None):
    """Runs a command, printing its output and exiting if it fails."""
    if description:
        print(f"{BOLD}--- {description} ---{RESET}")
    else:
        print(f"{BOLD}--- Running: {' '.join(command)} ---{RESET}")

    start_time = time.time()

    try:
        # Using check=True will raise CalledProcessError on non-zero exit codes
        result = subprocess.run(
            command, check=True, env=env, capture_output=True, text=True
        )

        # Print stdout if there's any
        if result.stdout.strip():
            print(result.stdout)

        elapsed_time = time.time() - start_time
        print_success(f"Completed in {elapsed_time:.2f} seconds")

    except subprocess.CalledProcessError as e:
        # Print any error output
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(f"{RED}{e.stderr}{RESET}")

        print_error(f"Command returned non-zero exit code {e.returncode}")
        sys.exit(e.returncode)

    except FileNotFoundError:
        print_error(
            f"Command not found: '{command[0]}'. Is it installed and in your PATH?"
        )
        print_warning(
            f"Hint: You may need to run 'pip install -r requirements-dev.txt'"
        )
        sys.exit(1)

    print()  # Empty line for readability


def check_environment():
    """Check if required environment variables and files exist."""
    print_header("Environment Check")

    # Check for .env file
    if not Path(".env").exists():
        print_warning(
            ".env file not found. Copy .env.example to .env and configure it."
        )
        # Don't exit, as some projects might use environment variables differently
    else:
        print_success(".env file found")

    # Check for required tools
    required_tools = ["black", "pytest", "alembic"]
    missing_tools = []

    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print_success(f"{tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
            print_error(f"{tool} is not installed")

    if missing_tools:
        print_error(f"\nMissing tools: {', '.join(missing_tools)}")
        print_warning("Install them with: pip install -r requirements-dev.txt")
        sys.exit(1)


def main():
    """Main function to run the test harness."""
    parser = argparse.ArgumentParser(description="Run test harness for the project")
    parser.add_argument(
        "--quick", action="store_true", help="Skip slow operations like migrations"
    )
    parser.add_argument(
        "--no-migrations", action="store_true", help="Skip database migrations"
    )
    parser.add_argument(
        "--no-format-check", action="store_true", help="Skip black formatting check"
    )
    parser.add_argument(
        "--coverage-min",
        type=int,
        default=80,
        help="Minimum coverage percentage required (default: 80)",
    )
    args = parser.parse_args()

    print_header("STARTING TEST & QUALITY HARNESS")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent.resolve()
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    # Check environment first
    check_environment()

    # Track overall status
    all_passed = True

    try:
        # 1. Check code formatting with Black
        if not args.no_format_check:
            run_command(
                ["black", "--check", "--diff", "."],
                description="Checking code formatting with Black",
            )
        else:
            print_warning("Skipping Black format check (--no-format-check)")

        # 2. Run linting (optional but recommended)
        # Uncomment if you use flake8 or ruff
        # run_command(["flake8", "app", "tests"], description="Running flake8 linter")
        # run_command(["ruff", "check", "."], description="Running ruff linter")

        # 3. Type checking (optional but recommended)
        # Uncomment if you use mypy
        # run_command(["mypy", "app"], description="Running mypy type checker")

        # 4. Ensure the test database schema is up-to-date
        if not args.quick and not args.no_migrations:
            run_command(
                ["alembic", "upgrade", "head"],
                env=os.environ,
                description="Applying migrations to test database",
            )
        else:
            print_warning("Skipping database migrations")

        # 5. Run the full test suite with coverage reporting
        pytest_args = [
            "pytest",
            "-v",  # Verbose output
            "--tb=short",  # Shorter traceback format
            f"--cov=app",  # Measure coverage for the 'app' directory
            f"--cov-fail-under={args.coverage_min}",  # Fail if coverage is below threshold
            "--cov-report=term-missing",  # Show missing lines
            "--cov-report=html",  # Generate HTML coverage report
        ]

        # Add color if terminal supports it
        if sys.stdout.isatty():
            pytest_args.append("--color=yes")

        run_command(pytest_args, description="Running pytest suite with coverage")

        # 6. Check for security vulnerabilities (optional)
        # Uncomment if you use safety
        # run_command(["safety", "check"], description="Checking for security vulnerabilities")

    except SystemExit as e:
        if e.code != 0:
            all_passed = False
            print_error("\n❌ TEST HARNESS FAILED!")
            raise

    if all_passed:
        print_header("✅ ALL CHECKS AND TESTS PASSED SUCCESSFULLY!")
        print_success("Your code is ready for commit!")
        print(
            f"\n💡 Tip: View detailed coverage report at: {project_root}/htmlcov/index.html"
        )


if __name__ == "__main__":
    main()
