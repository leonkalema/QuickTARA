<script lang="ts">
  import { onMount } from 'svelte';
  import { Database, TestTube, Play, CheckCircle, AlertCircle } from '@lucide/svelte';
  import settingsApi, { DatabaseType, type DatabaseConfig, type MigrationInfo } from '$lib/api/settings';
  import { notifications } from '$lib/stores/notifications';

  // Component state
  let loading = false;
  let testingConnection = false;
  let migrationLoading = false;
  let initDbLoading = false;
  let configModified = false;

  // Database configuration
  let dbType = DatabaseType.SQLITE;
  let dbPath = './quicktara.db';
  let dbHost = 'localhost';
  let dbPort = 5432;
  let dbName = 'quicktara';
  let dbUser = 'postgres';
  let dbPassword = '';

  // Store original values to detect changes
  let originalValues = {
    dbType: DatabaseType.SQLITE,
    dbPath: './quicktara.db',
    dbHost: 'localhost',
    dbPort: 5432,
    dbName: 'quicktara',
    dbUser: 'postgres',
    dbPassword: ''
  };

  // Migration status
  let migrationInfo: MigrationInfo = {
    current_revision: '',
    latest_revision: '',
    is_latest: true,
    pending_migrations: []
  };

  // Track configuration changes
  function updateConfigModified() {
    configModified = 
      dbType !== originalValues.dbType ||
      dbPath !== originalValues.dbPath ||
      dbHost !== originalValues.dbHost ||
      dbPort !== originalValues.dbPort ||
      dbName !== originalValues.dbName ||
      dbUser !== originalValues.dbUser ||
      dbPassword !== originalValues.dbPassword;
  }

  // Load current database configuration
  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    loading = true;
    try {
      const config = await settingsApi.getDatabaseConfig();
      
      // Update form with current configuration
      dbType = config.type;
      dbPath = config.path || './quicktara.db';
      dbHost = config.host || 'localhost';
      dbPort = config.port || (config.type === DatabaseType.POSTGRESQL ? 5432 : 3306);
      dbName = config.name || 'quicktara';
      dbUser = config.user || (config.type === DatabaseType.POSTGRESQL ? 'postgres' : 'root');
      dbPassword = config.password || '';

      // Update original values
      originalValues = { dbType, dbPath, dbHost, dbUser, dbPort, dbName, dbPassword };
      configModified = false;

      // Get migration status
      await loadMigrationStatus();
    } catch (error: any) {
      notifications.show(`Failed to load settings: ${error.message}`, 'error');
    } finally {
      loading = false;
    }
  }

  async function loadMigrationStatus() {
    try {
      migrationInfo = await settingsApi.getMigrationStatus();
    } catch (error: any) {
      notifications.show(`Failed to load migration status: ${error.message}`, 'error');
    }
  }

  // Test database connection
  async function testConnection() {
    testingConnection = true;
    console.log('Starting database connection test...');
    
    try {
      const config: DatabaseConfig = {
        type: dbType,
        path: dbType === DatabaseType.SQLITE ? dbPath : undefined,
        host: dbType !== DatabaseType.SQLITE ? dbHost : undefined,
        port: dbType !== DatabaseType.SQLITE ? (dbPort || (dbType === 'postgresql' ? 5432 : 3306)) : undefined,
        name: dbType !== DatabaseType.SQLITE ? dbName : undefined,
        user: dbType !== DatabaseType.SQLITE ? dbUser : undefined,
        password: dbType !== DatabaseType.SQLITE ? dbPassword : undefined,
      };

      console.log('Testing with config:', { ...config, password: config.password ? '***' : undefined });
      
      const result = await settingsApi.testDatabaseConnection(config);
      console.log('Test result:', result);
      
      if (result.success) {
        console.log('Showing success notification');
        notifications.show(result.message || 'Connection successful!', 'success');
      } else {
        console.log('Showing error notification');
        notifications.show(result.message || 'Connection failed.', 'error');
      }
    } catch (error: any) {
      console.error('Test connection error:', error);
      notifications.show(`Connection test failed: ${error.message}`, 'error');
    } finally {
      testingConnection = false;
      console.log('Test connection finished');
    }
  }

  // Save database configuration
  async function saveConfig() {
    loading = true;
    try {
      const config: DatabaseConfig = {
        type: dbType,
        path: dbType === DatabaseType.SQLITE ? dbPath : undefined,
        host: dbType !== DatabaseType.SQLITE ? dbHost : undefined,
        port: dbType !== DatabaseType.SQLITE ? (dbPort || (dbType === 'postgresql' ? 5432 : 3306)) : undefined,
        name: dbType !== DatabaseType.SQLITE ? dbName : undefined,
        user: dbType !== DatabaseType.SQLITE ? dbUser : undefined,
        password: dbType !== DatabaseType.SQLITE ? dbPassword : undefined,
      };

      await settingsApi.updateDatabaseConfig(config);
      notifications.show('Database settings saved successfully.', 'success');

      // Update original values
      originalValues = { dbType, dbPath, dbHost, dbUser, dbPort, dbName, dbPassword };
      configModified = false;

      // Refresh migration status
      await loadMigrationStatus();
    } catch (error: any) {
      notifications.show(`Failed to save settings: ${error.message}`, 'error');
    } finally {
      loading = false;
    }
  }

  // Run database migrations
  async function runMigrations() {
    migrationLoading = true;
    try {
      const result = await settingsApi.runMigrations();
      
      if (result.success) {
        notifications.show(result.message || 'Migrations applied successfully!', 'success');
        await loadMigrationStatus();
      } else {
        notifications.show(result.message || 'Failed to apply migrations.', 'error');
      }
    } catch (error: any) {
      notifications.show(`Failed to run migrations: ${error.message}`, 'error');
    } finally {
      migrationLoading = false;
    }
  }

  // Initialize database
  async function initializeDatabase() {
    initDbLoading = true;
    try {
      const result = await settingsApi.initializeDatabase();
      
      if (result.success) {
        notifications.show(result.message || 'Database initialized successfully!', 'success');
        await loadMigrationStatus();
      } else {
        notifications.show(result.message || 'Failed to initialize database.', 'error');
      }
    } catch (error: any) {
      notifications.show(`Failed to initialize database: ${error.message}`, 'error');
    } finally {
      initDbLoading = false;
    }
  }
</script>

<div class="database-settings">
  <div class="header">
    <div class="header-content">
      <Database class="w-5 h-5" style="color: var(--color-accent-primary);" />
      <h2>Database Configuration</h2>
    </div>
  </div>

  <!-- Database Configuration Form -->
  <div class="config-section">
    <h3>Connection Settings</h3>
    
    <div class="form-grid">
      <div class="form-group">
        <label for="db-type">Database Type</label>
        <select
          id="db-type"
          bind:value={dbType}
          on:change={updateConfigModified}
          disabled={loading}
        >
          <option value={DatabaseType.SQLITE}>SQLite (File-based)</option>
          <option value={DatabaseType.POSTGRESQL}>PostgreSQL</option>
          <option value={DatabaseType.MYSQL}>MySQL</option>
        </select>
      </div>

      {#if dbType === DatabaseType.SQLITE}
        <div class="form-group span-2">
          <label for="db-path">Database File Path</label>
          <input
            id="db-path"
            type="text"
            bind:value={dbPath}
            on:input={updateConfigModified}
            placeholder="./quicktara.db"
            disabled={loading}
          />
          <span class="help-text">Relative to application root or absolute path</span>
        </div>
      {:else}
        <div class="form-group">
          <label for="db-host">Host</label>
          <input
            id="db-host"
            type="text"
            bind:value={dbHost}
            on:input={updateConfigModified}
            placeholder="localhost"
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="db-port">Port</label>
          <input
            id="db-port"
            type="number"
            bind:value={dbPort}
            on:input={updateConfigModified}
            placeholder={dbType === DatabaseType.POSTGRESQL ? "5432" : "3306"}
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="db-name">Database Name</label>
          <input
            id="db-name"
            type="text"
            bind:value={dbName}
            on:input={updateConfigModified}
            placeholder="quicktara"
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="db-user">Username</label>
          <input
            id="db-user"
            type="text"
            bind:value={dbUser}
            on:input={updateConfigModified}
            placeholder={dbType === DatabaseType.POSTGRESQL ? "postgres" : "root"}
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="db-password">Password</label>
          <input
            id="db-password"
            type="password"
            bind:value={dbPassword}
            on:input={updateConfigModified}
            disabled={loading}
          />
        </div>
      {/if}
    </div>

    <div class="button-group">
      <button
        class="btn-secondary"
        on:click={testConnection}
        disabled={testingConnection}
      >
        <TestTube class="w-4 h-4" />
        {testingConnection ? 'Testing...' : 'Test Connection'}
      </button>

      <button
        class="btn-primary"
        on:click={saveConfig}
        disabled={loading || !configModified}
      >
        {loading ? 'Saving...' : 'Save Configuration'}
      </button>
    </div>
  </div>

  <!-- Migration Management -->
  <div class="migration-section">
    <h3>Database Migration Status</h3>
    
    {#if loading}
      <p>Loading migration status...</p>
    {:else}
      <div class="migration-info">
        <div class="info-item">
          <span class="label">Current Revision:</span>
          <span class="value">{migrationInfo.current_revision || 'Not initialized'}</span>
        </div>
        
        <div class="info-item">
          <span class="label">Latest Available:</span>
          <span class="value">{migrationInfo.latest_revision || 'Not available'}</span>
        </div>
        
        <div class="info-item">
          <span class="label">Status:</span>
          <span class="status {migrationInfo.is_latest ? 'up-to-date' : 'updates-available'}">
            {#if migrationInfo.is_latest}
              <CheckCircle class="w-4 h-4" />
              Up to date
            {:else}
              <AlertCircle class="w-4 h-4" />
              Updates available
            {/if}
          </span>
        </div>

        {#if migrationInfo.pending_migrations.length > 0}
          <div class="pending-migrations">
            <span class="label">Pending Migrations:</span>
            <ul>
              {#each migrationInfo.pending_migrations as migration}
                <li>{migration}</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>

      <div class="button-group">
        <button
          class="btn-primary"
          on:click={runMigrations}
          disabled={migrationLoading || migrationInfo.is_latest}
        >
          <Play class="w-4 h-4" />
          {migrationLoading ? 'Running...' : 'Run Migrations'}
        </button>

        <button
          class="btn-secondary"
          on:click={initializeDatabase}
          disabled={initDbLoading || (migrationInfo.current_revision !== 'Not initialized' && migrationInfo.current_revision !== 'Unknown')}
        >
          {initDbLoading ? 'Initializing...' : 'Initialize Database'}
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .database-settings {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .header {
    border-bottom: 1px solid var(--color-border-default);
    padding-bottom: 1rem;
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .header h2 {
    margin: 0;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .config-section, .migration-section {
    background: var(--color-bg-surface);
    border: 1px solid var(--color-border-default);
    border-radius: 8px;
    padding: 1.5rem;
  }

  .config-section h3, .migration-section h3 {
    margin: 0 0 1.5rem 0;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .span-2 {
    grid-column: span 2;
  }

  label {
    font-weight: 500;
    color: var(--color-text-secondary);
    font-size: 0.6875rem;
  }

  input, select {
    padding: 0.625rem 0.75rem;
    border: 1px solid var(--color-border-default);
    border-radius: 6px;
    font-size: 0.75rem;
    background: var(--color-bg-inset);
    color: var(--color-text-primary);
  }

  input:focus, select:focus {
    outline: none;
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent-primary) 20%, transparent);
  }

  .help-text {
    font-size: 0.6875rem;
    color: var(--color-text-tertiary);
  }

  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .btn-primary, .btn-secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.75rem;
    transition: all 0.2s;
  }

  .btn-primary {
    background: var(--color-accent-primary);
    color: var(--color-text-inverse);
  }

  .btn-primary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .btn-primary:not(:disabled):hover {
    filter: brightness(1.1);
  }

  .btn-secondary {
    background: var(--color-bg-elevated);
    color: var(--color-text-secondary);
    border: 1px solid var(--color-border-default);
  }

  .btn-secondary:not(:disabled):hover {
    filter: brightness(1.1);
  }

  .migration-info {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .label {
    font-weight: 500;
    color: var(--color-text-secondary);
    font-size: 0.75rem;
  }

  .value {
    color: var(--color-text-primary);
    font-size: 0.75rem;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
  }

  .up-to-date {
    color: var(--color-status-accepted-text, #10b981);
  }

  .updates-available {
    color: var(--color-status-draft-text, #f59e0b);
  }

  .pending-migrations {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .pending-migrations ul {
    margin: 0;
    padding-left: 1.5rem;
    color: var(--color-text-tertiary);
  }

  .pending-migrations li {
    font-size: 0.75rem;
  }
</style>
