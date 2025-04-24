"""
Configuration settings loader
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent / "default.yaml"


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    """
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        return {}


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables
    """
    config = {}
    
    # Database settings
    if db_type := os.environ.get("QUICKTARA_DB_TYPE"):
        config.setdefault("database", {})["type"] = db_type
    if db_path := os.environ.get("QUICKTARA_DB_PATH"):
        config.setdefault("database", {})["path"] = db_path
    if db_host := os.environ.get("QUICKTARA_DB_HOST"):
        config.setdefault("database", {})["host"] = db_host
    if db_port := os.environ.get("QUICKTARA_DB_PORT"):
        config.setdefault("database", {})["port"] = int(db_port)
    if db_name := os.environ.get("QUICKTARA_DB_NAME"):
        config.setdefault("database", {})["name"] = db_name
    if db_user := os.environ.get("QUICKTARA_DB_USER"):
        config.setdefault("database", {})["user"] = db_user
    if db_password := os.environ.get("QUICKTARA_DB_PASSWORD"):
        config.setdefault("database", {})["password"] = db_password
    
    # Server settings
    if server_host := os.environ.get("QUICKTARA_SERVER_HOST"):
        config.setdefault("server", {})["host"] = server_host
    if server_port := os.environ.get("QUICKTARA_SERVER_PORT"):
        config.setdefault("server", {})["port"] = int(server_port)
    if server_debug := os.environ.get("QUICKTARA_SERVER_DEBUG"):
        config.setdefault("server", {})["debug"] = server_debug.lower() == "true"
    
    # Storage settings
    if uploads_dir := os.environ.get("QUICKTARA_UPLOADS_DIR"):
        config.setdefault("storage", {})["uploads_dir"] = uploads_dir
    if reports_dir := os.environ.get("QUICKTARA_REPORTS_DIR"):
        config.setdefault("storage", {})["reports_dir"] = reports_dir
    
    # Logging settings
    if log_level := os.environ.get("QUICKTARA_LOG_LEVEL"):
        config.setdefault("logging", {})["level"] = log_level
    if log_file := os.environ.get("QUICKTARA_LOG_FILE"):
        config.setdefault("logging", {})["file"] = log_file
    
    return config


def load_settings(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load settings from default config, custom config file, and environment variables
    """
    # Start with default config
    config = load_yaml_config(DEFAULT_CONFIG_PATH)
    
    # Override with custom config if provided
    if config_path and config_path.exists():
        custom_config = load_yaml_config(config_path)
        deep_update(config, custom_config)
    
    # Override with environment variables
    env_config = load_env_config()
    deep_update(config, env_config)
    
    return config


def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """
    Recursively update a dictionary
    """
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


def configure_logging(config: Dict[str, Any]) -> None:
    """
    Configure logging based on settings
    """
    log_config = config.get("logging", {})
    log_level_str = log_config.get("level", "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if log_file := log_config.get("file"):
        logging.basicConfig(
            level=log_level,
            format=log_format,
            filename=log_file,
            filemode="a"
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=log_format
        )
