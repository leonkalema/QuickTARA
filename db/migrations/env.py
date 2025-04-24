from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Add the parent directory to sys.path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Base and models to ensure they're all included in the metadata
from db.base import Base
# Import all models that extend Base
from db.base import Component, Analysis, ComponentAnalysis, Report, ReviewDecision

# Update the SQLAlchemy URL based on environment or settings file
from db.session import get_database_url

# Try to load configuration file
try:
    from config.settings import load_settings
    settings = load_settings()
    sqlalchemy_url = get_database_url(settings)
    config.set_main_option("sqlalchemy.url", sqlalchemy_url)
except ImportError:
    # Use default from alembic.ini
    sqlalchemy_url = config.get_main_option("sqlalchemy.url")

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Add 'compare_type' to detect column type changes
            compare_type=True,
            # Add render_as_batch for better SQLite support with ALTER
            render_as_batch=True,
            # Skip objects that already exist in the database
            include_object=lambda obj, name, type_, reflected, compare_to:
                not reflected or type_ != "table" or obj.name not in connection.engine.table_names()
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
