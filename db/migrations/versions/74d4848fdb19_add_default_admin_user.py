"""add_default_admin_user

Revision ID: 74d4848fdb19
Revises: e467b7ba4c51
Create Date: 2025-01-07 15:15:33.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, DateTime
import uuid
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '74d4848fdb19'
down_revision = 'e467b7ba4c51'
branch_labels = None
depends_on = None


def upgrade():
    # Check if users table exists, if not skip this migration
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'users' not in inspector.get_table_names():
        print("Users table doesn't exist yet. Skipping default admin user creation.")
        print("Run this migration again after the users table is created.")
        return
    
    # Insert default admin user only if it doesn't exist
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users WHERE email = 'admin@quicktara.local'"))
    count = result.scalar()
    
    if count > 0:
        print("Default admin user already exists. Skipping creation.")
        return
    
    # Insert default admin user
    users_table = table('users',
        column('user_id', String),
        column('email', String),
        column('hashed_password', String),
        column('full_name', String),
        column('role', String),
        column('is_active', Boolean),
        column('created_at', DateTime),
        column('updated_at', DateTime)
    )
    
    # Hash the default password 'admin123' using bcrypt
    # This is the bcrypt hash for 'admin123'
    hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S8VyDe'
    
    now = datetime.utcnow()
    
    op.bulk_insert(users_table, [
        {
            'user_id': str(uuid.uuid4()),
            'email': 'admin@quicktara.local',
            'hashed_password': hashed_password,
            'full_name': 'System Administrator',
            'role': 'Tool Admin',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
    ])
    
    print("=" * 60)
    print("DEFAULT ADMIN USER CREATED")
    print("=" * 60)
    print("Email: admin@quicktara.local")
    print("Password: admin123")
    print("Role: Tool Admin")
    print("")
    print("⚠️  SECURITY WARNING: Change this password immediately after first login!")
    print("=" * 60)


def downgrade():
    # Remove the default admin user
    op.execute("DELETE FROM users WHERE email = 'admin@quicktara.local'")
    
    # Optionally drop the users table if it was created by this migration
    # op.drop_table('users')
