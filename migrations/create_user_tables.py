"""
Create user authentication tables
Migration for user management and RBAC system
"""

import sqlite3
import uuid
from datetime import datetime

def create_user_tables(db_path: str):
    """Create all user-related tables"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Organizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                organization_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                domain TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                is_verified BOOLEAN DEFAULT 0,
                is_superuser BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failed_login_attempts TEXT DEFAULT '0',
                locked_until TIMESTAMP
            )
        """)
        
        # User-Organization junction table (many-to-many with roles)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_organizations (
                user_id TEXT,
                organization_id TEXT,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, organization_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
            )
        """)
        
        # Refresh tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_info TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # Permissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                resource TEXT NOT NULL,
                action TEXT NOT NULL
            )
        """)
        
        # Role-Permission junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                role TEXT,
                permission_id TEXT,
                organization_scope BOOLEAN DEFAULT 1,
                PRIMARY KEY (role, permission_id),
                FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_orgs_user ON user_organizations(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_orgs_org ON user_organizations(organization_id)")
        
        # Insert default organization
        default_org_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO organizations (organization_id, name, description, domain)
            VALUES (?, ?, ?, ?)
        """, (default_org_id, "Default Organization", "Default organization for QuickTARA", "quicktara.local"))
        
        # Insert basic permissions
        permissions = [
            # User management
            ("users:create", "Create users", "users", "create"),
            ("users:read", "Read users", "users", "read"),
            ("users:update", "Update users", "users", "update"),
            ("users:delete", "Delete users", "users", "delete"),
            
            # Organization management
            ("organizations:create", "Create organizations", "organizations", "create"),
            ("organizations:read", "Read organizations", "organizations", "read"),
            ("organizations:update", "Update organizations", "organizations", "update"),
            ("organizations:delete", "Delete organizations", "organizations", "delete"),
            
            # Product management
            ("products:create", "Create products", "products", "create"),
            ("products:read", "Read products", "products", "read"),
            ("products:update", "Update products", "products", "update"),
            ("products:delete", "Delete products", "products", "delete"),
            
            # Asset management
            ("assets:create", "Create assets", "assets", "create"),
            ("assets:read", "Read assets", "assets", "read"),
            ("assets:update", "Update assets", "assets", "update"),
            ("assets:delete", "Delete assets", "assets", "delete"),
            
            # Damage scenarios
            ("damage_scenarios:create", "Create damage scenarios", "damage_scenarios", "create"),
            ("damage_scenarios:read", "Read damage scenarios", "damage_scenarios", "read"),
            ("damage_scenarios:update", "Update damage scenarios", "damage_scenarios", "update"),
            ("damage_scenarios:delete", "Delete damage scenarios", "damage_scenarios", "delete"),
            
            # Threat scenarios
            ("threat_scenarios:create", "Create threat scenarios", "threat_scenarios", "create"),
            ("threat_scenarios:read", "Read threat scenarios", "threat_scenarios", "read"),
            ("threat_scenarios:update", "Update threat scenarios", "threat_scenarios", "update"),
            ("threat_scenarios:delete", "Delete threat scenarios", "threat_scenarios", "delete"),
            
            # Attack paths
            ("attack_paths:create", "Create attack paths", "attack_paths", "create"),
            ("attack_paths:read", "Read attack paths", "attack_paths", "read"),
            ("attack_paths:update", "Update attack paths", "attack_paths", "update"),
            ("attack_paths:delete", "Delete attack paths", "attack_paths", "delete"),
            
            # Risk treatments
            ("risk_treatments:create", "Create risk treatments", "risk_treatments", "create"),
            ("risk_treatments:read", "Read risk treatments", "risk_treatments", "read"),
            ("risk_treatments:update", "Update risk treatments", "risk_treatments", "update"),
            ("risk_treatments:delete", "Delete risk treatments", "risk_treatments", "delete"),
            ("risk_treatments:approve", "Approve risk treatments", "risk_treatments", "approve"),
            
            # Reports
            ("reports:generate", "Generate reports", "reports", "generate"),
            ("reports:read", "Read reports", "reports", "read"),
            ("reports:approve", "Approve reports", "reports", "approve"),
            
            # System administration
            ("system:configure", "Configure system", "system", "configure"),
            ("system:backup", "Backup system", "system", "backup"),
            ("system:monitor", "Monitor system", "system", "monitor"),
            
            # Compliance and audit
            ("compliance:review", "Review compliance", "compliance", "review"),
            ("compliance:audit", "Audit compliance", "compliance", "audit"),
            ("audit_trail:read", "Read audit trail", "audit_trail", "read"),
            ("risk_acceptance:approve", "Approve risk acceptance", "risk_acceptance", "approve")
        ]
        
        for perm_name, description, resource, action in permissions:
            perm_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT OR IGNORE INTO permissions (permission_id, name, description, resource, action)
                VALUES (?, ?, ?, ?, ?)
            """, (perm_id, perm_name, description, resource, action))
        
        # Create default admin user
        admin_user_id = str(uuid.uuid4())
        # Default password: "admin123" (should be changed immediately)
        # This is bcrypt hash of "admin123"
        admin_password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S7ZOvG"
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (
                user_id, email, username, first_name, last_name, 
                hashed_password, status, is_verified, is_superuser
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_user_id, "admin@quicktara.local", "admin", "System", "Administrator",
            admin_password_hash, "active", 1, 1
        ))
        
        # Assign admin to default organization
        cursor.execute("""
            INSERT OR IGNORE INTO user_organizations (user_id, organization_id, role)
            VALUES (?, ?, ?)
        """, (admin_user_id, default_org_id, "tool_admin"))
        
        conn.commit()
        print("✅ User authentication tables created successfully")
        print("📧 Default admin user: admin@quicktara.local")
        print("🔑 Default password: admin123 (CHANGE IMMEDIATELY)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating user tables: {e}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "quicktara.db"
    
    create_user_tables(db_path)
