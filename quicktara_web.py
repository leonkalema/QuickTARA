#!/usr/bin/env python3
"""
QuickTARA Web - Main entry point
A local-first web application for automotive security analysis
"""
import os
import argparse
import logging
import uvicorn
from pathlib import Path

from config.settings import load_settings, configure_logging
from db.session import init_db
from api.app import create_app

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for QuickTARA Web
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="QuickTARA Web - Automotive Security Analysis")
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file",
        type=str,
        default=None
    )
    parser.add_argument(
        "--host",
        help="Host to bind the server to",
        type=str,
        default=None
    )
    parser.add_argument(
        "--port",
        help="Port to bind the server to",
        type=int,
        default=None
    )
    parser.add_argument(
        "--db",
        help="Database connection string or path",
        type=str,
        default=None
    )
    parser.add_argument(
        "--debug",
        help="Enable debug mode",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config) if args.config else None
    settings = load_settings(config_path)
    
    # Override settings with command line arguments
    if args.host:
        settings.setdefault("server", {})["host"] = args.host
    if args.port:
        settings.setdefault("server", {})["port"] = args.port
    if args.db:
        # Simple handling - treat as SQLite path or full connection string
        if args.db.startswith("sqlite:") or args.db.startswith("postgresql:") or args.db.startswith("mysql:"):
            # It's a connection string - parse it
            if args.db.startswith("sqlite:"):
                settings.setdefault("database", {})["type"] = "sqlite"
                settings.setdefault("database", {})["path"] = args.db.split("sqlite:///")[1]
            else:
                # Just store the connection string for later use
                os.environ["DATABASE_URL"] = args.db
        else:
            # Assume it's a SQLite path
            settings.setdefault("database", {})["type"] = "sqlite"
            settings.setdefault("database", {})["path"] = args.db
    
    if args.debug:
        settings.setdefault("server", {})["debug"] = True
        settings.setdefault("logging", {})["level"] = "debug"
    
    # Configure logging
    configure_logging(settings)
    
    # Initialize database
    logger.info("Initializing database...")
    init_db(settings)
    
    # Create FastAPI application
    logger.info("Creating FastAPI application...")
    app = create_app(settings)
    
    # Get server settings
    server_settings = settings.get("server", {})
    host = server_settings.get("host", "127.0.0.1")
    port = int(server_settings.get("port", 8080))
    debug = server_settings.get("debug", False)
    
    # Start server
    logger.info(f"Starting server on {host}:{port} (debug={debug})...")
    uvicorn.run(
        "api.app:create_app",
        host=host,
        port=port,
        reload=debug,
        factory=True,
        log_level="debug" if debug else "info"
    )


if __name__ == "__main__":
    main()
