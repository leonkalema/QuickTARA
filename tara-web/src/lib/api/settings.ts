/**
 * Settings API Client
 * 
 * Handles API calls related to application settings and database configuration
 */

/**
 * Database types supported by the application
 */
export enum DatabaseType {
  SQLITE = 'sqlite',
  POSTGRESQL = 'postgresql',
  MYSQL = 'mysql'
}

/**
 * Database connection configuration
 */
export interface DatabaseConfig {
  type: DatabaseType;
  path?: string; // For SQLite
  host?: string; // For PostgreSQL/MySQL
  port?: number; // For PostgreSQL/MySQL
  name?: string; // Database name for PostgreSQL/MySQL
  user?: string; // For PostgreSQL/MySQL
  password?: string; // For PostgreSQL/MySQL
}

/**
 * Database migration information
 */
export interface MigrationInfo {
  current_revision: string;
  latest_revision: string;
  is_latest: boolean;
  pending_migrations: string[];
}

/**
 * API Response types
 */
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

/**
 * Settings API client
 */
import { API_BASE_URL } from '$lib/config';

const settingsApi = {
  /**
   * Get current database configuration
   */
  async getDatabaseConfig(): Promise<DatabaseConfig> {
    const response = await fetch(`${API_BASE_URL}/settings/database`);
    if (!response.ok) {
      throw new Error(`Failed to get database config: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Update database configuration
   */
  async updateDatabaseConfig(config: DatabaseConfig): Promise<DatabaseConfig> {
    const response = await fetch(`${API_BASE_URL}/settings/database`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config)
    });
    if (!response.ok) {
      throw new Error(`Failed to update database config: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Test database connection
   */
  async testDatabaseConnection(config: DatabaseConfig): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/settings/database/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config)
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return result;
  },

  /**
   * Get database migration status
   */
  async getMigrationStatus(): Promise<MigrationInfo> {
    const response = await fetch(`${API_BASE_URL}/settings/database/migrations`);
    if (!response.ok) {
      throw new Error(`Failed to get migration status: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Run database migrations
   */
  async runMigrations(): Promise<{ success: boolean; message: string; migrations_applied: string[] }> {
    const response = await fetch(`${API_BASE_URL}/settings/database/migrations/upgrade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    if (!response.ok) {
      throw new Error(`Failed to run migrations: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Initialize a new database
   */
  async initializeDatabase(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/settings/database/initialize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    if (!response.ok) {
      throw new Error(`Failed to initialize database: ${response.statusText}`);
    }
    return response.json();
  }
};

export default settingsApi;
