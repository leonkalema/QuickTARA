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
from sqlalchemy import String, Boolean, DateTime


# revision identifiers, used by Alembic.
revision = '74d4848fdb19'
down_revision = 'e467b7ba4c51'
branch_labels = None
depends_on = None


ADMIN_EMAIL = 'admin@quicktara.local'
CREDENTIALS_FILENAME = 'quicktara-initial-credentials.txt'


def _generate_password() -> str:
    """24-char URL-safe random password (~144 bits of entropy)."""
    return secrets.token_urlsafe(18)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def _write_credentials_file(email: str, password: str) -> Path:
    """Write the bootstrap credentials to a 0600 file in the project root."""
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
        # Best-effort on platforms (e.g. Windows) without POSIX perms
        pass
    return target


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'users' not in inspector.get_table_names():
        print("Users table doesn't exist yet. Skipping default admin user creation.")
        print("Run this migration again after the users table is created.")
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
        column('hashed_password', String),
        column('full_name', String),
        column('role', String),
        column('is_active', Boolean),
        column('created_at', DateTime),
        column('updated_at', DateTime),
    )

    password = _generate_password()
    hashed_password = _hash_password(password)
    now = datetime.utcnow()

    op.bulk_insert(users_table, [
        {
            'user_id': str(uuid.uuid4()),
            'email': ADMIN_EMAIL,
            'hashed_password': hashed_password,
            'full_name': 'System Administrator',
            'role': 'Tool Admin',
            'is_active': True,
            'created_at': now,
            'updated_at': now,
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
