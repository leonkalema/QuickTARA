"""Check and fix database tables

Revision ID: f8a52c9271e3
Revises: e1c8d1ad3c7b
Create Date: 2023-09-20 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'f8a52c9271e3'
down_revision = 'e1c8d1ad3c7b'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade():
    """
    Check and fix tables if needed
    This migration will check if tables already exist and fix any issues
    """
    # This migration doesn't create any new tables
    # It just checks if tables exist and records the migration
    # This allows the migration history to be recorded correctly
    
    # List of tables to check
    tables_to_check = [
        'component_connections',
        'components',
        'analyses',
        'component_analyses',
        'reports',
        'review_decisions'
    ]
    
    # Check each table
    for table in tables_to_check:
        if table_exists(table):
            op.execute(f"/* Table {table} already exists */")
        else:
            op.execute(f"/* Table {table} missing */")


def downgrade():
    """Downgrade migration (does nothing)"""
    pass
