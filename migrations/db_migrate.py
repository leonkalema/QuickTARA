#!/usr/bin/env python3
"""
QuickTARA Database Migration Tool

This script provides commands for managing database migrations with Alembic.
"""
import argparse
import os
import sys
import subprocess
from pathlib import Path
import logging
from config.settings import load_settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("db_migrate")

# Get the project root directory
project_dir = Path(__file__).parent.absolute()


def run_alembic_command(command, **kwargs):
    """
    Run an Alembic command
    
    Args:
        command: Alembic command to run
        **kwargs: Additional arguments for the command
    """
    args = [sys.executable, "-m", "alembic"]
    args.extend(command.split())
    
    # Add any additional arguments
    for k, v in kwargs.items():
        if v is not None:
            args.extend([f"--{k.replace('_', '-')}", str(v)])
    
    logger.info(f"Running: {' '.join(args)}")
    
    try:
        result = subprocess.run(
            args,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(e.stderr)
        return False


def create_migration(message, autogenerate=True):
    """
    Create a new migration
    
    Args:
        message: Migration message/description
        autogenerate: Whether to autogenerate migration based on schema changes
    """
    cmd = "revision"
    if autogenerate:
        return run_alembic_command(cmd, autogenerate=True, message=message)
    else:
        return run_alembic_command(cmd, message=message)


def upgrade_db(revision="head"):
    """
    Upgrade database to a specific revision
    
    Args:
        revision: Target revision (default: "head")
    """
    return run_alembic_command(f"upgrade {revision}")


def downgrade_db(revision="-1"):
    """
    Downgrade database to a specific revision
    
    Args:
        revision: Target revision (default: "-1", one revision back)
    """
    return run_alembic_command(f"downgrade {revision}")


def show_history():
    """Show migration history"""
    return run_alembic_command("history")


def show_current():
    """Show current revision"""
    return run_alembic_command("current")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database migration tool for QuickTARA")
    subparsers = parser.add_subparsers(dest="command", help="Migration command")
    
    # Create migration
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration description")
    create_parser.add_argument("--no-autogenerate", action="store_true", help="Don't autogenerate migration")
    
    # Upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Target revision (default: head)")
    
    # Downgrade
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", nargs="?", default="-1", help="Target revision (default: -1)")
    
    # History
    subparsers.add_parser("history", help="Show migration history")
    
    # Current
    subparsers.add_parser("current", help="Show current revision")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "create":
        create_migration(args.message, not args.no_autogenerate)
    elif args.command == "upgrade":
        upgrade_db(args.revision)
    elif args.command == "downgrade":
        downgrade_db(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
