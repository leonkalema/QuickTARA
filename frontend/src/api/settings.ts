/**
 * Settings API Client
 * 
 * Handles API calls related to application settings and database configuration
 */

import apiClient from './index';

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
 * Settings API client
 */
const settingsApi = {
  /**
   * Get current database configuration
   * @returns Current database configuration
   */
  async getDatabaseConfig(): Promise<DatabaseConfig> {
    return apiClient.get<DatabaseConfig>('/settings/database');
  },

  /**
   * Update database configuration
   * @param config New database configuration
   * @returns Updated database configuration
   */
  async updateDatabaseConfig(config: DatabaseConfig): Promise<DatabaseConfig> {
    return apiClient.post<DatabaseConfig>('/settings/database', config);
  },

  /**
   * Test database connection
   * @param config Database configuration to test
   * @returns Connection status
   */
  async testDatabaseConnection(config: DatabaseConfig): Promise<{ success: boolean; message: string }> {
    return apiClient.post<{ success: boolean; message: string }>('/settings/database/test', config);
  },

  /**
   * Get database migration status
   * @returns Migration information
   */
  async getMigrationStatus(): Promise<MigrationInfo> {
    return apiClient.get<MigrationInfo>('/settings/database/migrations');
  },

  /**
   * Run database migrations
   * @returns Migration results
   */
  async runMigrations(): Promise<{ success: boolean; message: string; migrations_applied: string[] }> {
    return apiClient.post<{ success: boolean; message: string; migrations_applied: string[] }>(
      '/settings/database/migrations/upgrade'
    );
  },

  /**
   * Initialize a new database
   * @returns Initialization results
   */
  async initializeDatabase(): Promise<{ success: boolean; message: string }> {
    return apiClient.post<{ success: boolean; message: string }>('/settings/database/initialize');
  }
};

export default settingsApi;
