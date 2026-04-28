"""add_default_admin_user

Revision ID: 74d4848fdb19
Revises: e467b7ba4c51
Create Date: 2025-01-07 15:15:33.000000

"""
import os
import secrets
import stat
import uuid
from datetime import datetime
from pathlib import Path

import bcrypt
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum


# revision identifiers, used by Alembic.
revision = '74d4848fdb19'
down_revision = 'e467b7ba4c51'
branch_labels = None
depends_on = None


ADMIN_EMAIL = os.environ.get('QUICKTARA_ADMIN_EMAIL', 'admin@quicktara.local')
CREDENTIALS_FILENAME = 'quicktara-initial-credentials.txt'


def _generate_password() -> str:
    return secrets.token_urlsafe(18)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def _write_credentials_file(email: str, password: str) -> Path:
    target = Path(os.getcwd()) / CREDENTIALS_FILENAME
    target.write_text(
        "QuickTARA — initial bootstrap credentials\n"
        "==========================================\n"
        f"Email:    {email}\n"
        f"Password: {password}\n"
        "\n"
        "Sign in at the URL printed by the deploy script and change this\n"
        "password immediately under Settings -> My Account, then DELETE\n"
        "this file.\n",
        encoding='utf-8',
    )
    try:
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError:
        pass
    return target


def _ensure_auth_tables(connection, inspector):
    """Create auth tables if they don't exist (they're ORM-only, not in the initial schema migration)."""
    existing = inspector.get_table_names()

    if 'organizations' not in existing:
        op.create_table(
            'organizations',
            sa.Column('organization_id', String, primary_key=True),
            sa.Column('name', String(255), nullable=False),
            sa.Column('description', String(500)),
            sa.Column('domain', String(255)),
            sa.Column('is_active', Boolean, default=True),
            sa.Column('created_at', DateTime),
            sa.Column('updated_at', DateTime),
        )

    if 'users' not in existing:
        op.create_table(
            'users',
            sa.Column('user_id', String, primary_key=True),
            sa.Column('email', String(255), nullable=False, unique=True),
            sa.Column('username', String(100), nullable=False, unique=True),
            sa.Column('first_name', String(100), nullable=False),
            sa.Column('last_name', String(100), nullable=False),
            sa.Column('hashed_password', String(255), nullable=False),
            sa.Column('status', String(20), default='active'),
            sa.Column('is_verified', Boolean, default=True),
            sa.Column('is_superuser', Boolean, default=False),
            sa.Column('created_at', DateTime),
            sa.Column('updated_at', DateTime),
            sa.Column('last_login', DateTime),
            sa.Column('password_changed_at', DateTime),
            sa.Column('failed_login_attempts', String, default='0'),
            sa.Column('locked_until', DateTime),
        )

    if 'user_organizations' not in existing:
        op.create_table(
            'user_organizations',
            sa.Column('user_id', String, sa.ForeignKey('users.user_id'), primary_key=True),
            sa.Column('organization_id', String, sa.ForeignKey('organizations.organization_id'), primary_key=True),
            sa.Column('role', String(50), nullable=False),
            sa.Column('created_at', DateTime),
        )

    if 'refresh_tokens' not in existing:
        op.create_table(
            'refresh_tokens',
            sa.Column('token_id', String, primary_key=True),
            sa.Column('user_id', String, sa.ForeignKey('users.user_id'), nullable=False),
            sa.Column('token_hash', String(255), nullable=False),
            sa.Column('expires_at', DateTime, nullable=False),
            sa.Column('is_revoked', Boolean, default=False),
            sa.Column('created_at', DateTime),
            sa.Column('device_info', String(500)),
            sa.Column('ip_address', String(45)),
            sa.Column('user_agent', String(500)),
        )


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    _ensure_auth_tables(connection, inspector)

    # Re-inspect after potential table creation
    inspector = sa.inspect(connection)
    if 'users' not in inspector.get_table_names():
        print("ERROR: Could not create users table. Skipping admin user creation.")
        return

    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    )
    if result.scalar() > 0:
        print("Default admin user already exists. Skipping creation.")
        return

    users_table = table('users',
        column('user_id', String),
        column('email', String),
        column('username', String),
        column('first_name', String),
        column('last_name', String),
        column('hashed_password', String),
        column('status', String),
        column('is_verified', Boolean),
        column('is_superuser', Boolean),
        column('created_at', DateTime),
        column('updated_at', DateTime),
        column('password_changed_at', DateTime),
        column('failed_login_attempts', String),
    )

    password = _generate_password()
    hashed_password = _hash_password(password)
    now = datetime.utcnow()

    op.bulk_insert(users_table, [
        {
            'user_id': str(uuid.uuid4()),
            'email': ADMIN_EMAIL,
            'username': 'admin',
            'first_name': 'System',
            'last_name': 'Administrator',
            'hashed_password': hashed_password,
            'status': 'active',
            'is_verified': True,
            'is_superuser': True,
            'created_at': now,
            'updated_at': now,
            'password_changed_at': now,
            'failed_login_attempts': '0',
        }
    ])

    creds_path = _write_credentials_file(ADMIN_EMAIL, password)

    banner = "=" * 60
    print(banner)
    print("INITIAL ADMIN USER CREATED")
    print(banner)
    print(f"Email:        {ADMIN_EMAIL}")
    print(f"Credentials:  {creds_path}")
    print("Permissions:  0600 (owner read/write only)")
    print("")
    print("Sign in once, change the password under Settings -> My")
    print("Account, then DELETE the credentials file.")
    print(banner)


def downgrade():
    op.execute(sa.text("DELETE FROM users WHERE email = :email").bindparams(email=ADMIN_EMAIL))
