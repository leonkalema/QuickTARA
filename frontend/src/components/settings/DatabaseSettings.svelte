<script lang="ts">
  import { onMount } from 'svelte';
  import settingsApi, { DatabaseType } from '../../api/settings';
  
  // Component state
  let loading = false;
  let testingConnection = false;
  let migrationLoading = false;
  let initDbLoading = false;
  let errorMessage = '';
  let successMessage = '';
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
    dbType: 'sqlite',
    dbPath: './quicktara.db',
    dbHost: 'localhost',
    dbPort: 5432,
    dbName: 'quicktara',
    dbUser: 'postgres',
    dbPassword: ''
  };
  
  // Track when configuration changes
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
  
  // Migration status
  let currentRevision = '';
  let latestRevision = '';
  let isLatest = true;
  let pendingMigrations: string[] = [];
  
  // Load current database configuration
  onMount(async () => {
    loading = true;
    errorMessage = '';
    
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
      
      // Update original values to track changes
      originalValues = {
        dbType,
        dbPath,
        dbHost,
        dbUser,
        dbPort,
        dbName,
        dbPassword
      };
      configModified = false;
      
      // Get migration status
      await loadMigrationStatus();
    } catch (error: any) {
      errorMessage = `Failed to load settings: ${error.message}`;
    } finally {
      loading = false;
    }
  });
  
  // Load migration status
  async function loadMigrationStatus() {
    try {
      const status = await settingsApi.getMigrationStatus();
      currentRevision = status.current_revision;
      latestRevision = status.latest_revision;
      isLatest = status.is_latest;
      pendingMigrations = status.pending_migrations;
    } catch (error: any) {
      errorMessage = `Failed to load migration status: ${error.message}`;
    }
  }
  
  // Test database connection
  async function testConnection() {
    testingConnection = true;
    errorMessage = '';
    successMessage = '';
    
    try {
      const config = {
        type: dbType,
        path: dbType === DatabaseType.SQLITE ? dbPath : undefined,
        host: dbType !== DatabaseType.SQLITE ? dbHost : undefined,
        port: dbType !== DatabaseType.SQLITE ? dbPort : undefined,
        name: dbType !== DatabaseType.SQLITE ? dbName : undefined,
        user: dbType !== DatabaseType.SQLITE ? dbUser : undefined,
        password: dbType !== DatabaseType.SQLITE ? dbPassword : undefined,
      };
      
      const result = await settingsApi.testDatabaseConnection(config);
      
      if (result.success) {
        successMessage = result.message || 'Connection successful!';
      } else {
        errorMessage = result.message || 'Connection failed.';
      }
    } catch (error: any) {
      errorMessage = `Connection test failed: ${error.message}`;
    } finally {
      testingConnection = false;
    }
  }
  
  // Save database configuration
  async function saveConfig() {
    loading = true;
    errorMessage = '';
    successMessage = '';
    
    try {
      const config = {
        type: dbType,
        path: dbType === DatabaseType.SQLITE ? dbPath : undefined,
        host: dbType !== DatabaseType.SQLITE ? dbHost : undefined,
        port: dbType !== DatabaseType.SQLITE ? dbPort : undefined,
        name: dbType !== DatabaseType.SQLITE ? dbName : undefined,
        user: dbType !== DatabaseType.SQLITE ? dbUser : undefined,
        password: dbType !== DatabaseType.SQLITE ? dbPassword : undefined,
      };
      
      await settingsApi.updateDatabaseConfig(config);
      successMessage = 'Database settings saved successfully.';
      
      // Update original values to match current values
      originalValues = {
        dbType,
        dbPath,
        dbHost,
        dbUser,
        dbPort,
        dbName,
        dbPassword
      };
      configModified = false;
      
      // Refresh migration status
      await loadMigrationStatus();
    } catch (error: any) {
      errorMessage = `Failed to save settings: ${error.message}`;
    } finally {
      loading = false;
    }
  }
  
  // Run database migrations
  async function runMigrations() {
    migrationLoading = true;
    errorMessage = '';
    successMessage = '';
    
    try {
      const result = await settingsApi.runMigrations();
      
      if (result.success) {
        successMessage = result.message || 'Migrations applied successfully!';
        
        // Refresh migration status
        await loadMigrationStatus();
        
        // Handle the case where tables already exist
        if (result.message && (result.message.includes('already exist') || result.message.includes('skipping migration'))) {
          isLatest = true;
        }
      } else {
        // If the error is just that tables already exist, treat it as success
        if (result.message && result.message.includes('already exist')) {
          successMessage = 'Database is already configured. No migration needed.';
          isLatest = true;
        } else {
          errorMessage = result.message || 'Failed to apply migrations.';
        }
      }
    } catch (error: any) {
      errorMessage = `Failed to run migrations: ${error.message}`;
    } finally {
      migrationLoading = false;
    }
  }
  
  // Initialize database
  async function initializeDatabase() {
    initDbLoading = true;
    errorMessage = '';
    successMessage = '';
    
    try {
      const result = await settingsApi.initializeDatabase();
      
      if (result.success) {
        successMessage = result.message || 'Database initialized successfully!';
        
        // Refresh migration status
        await loadMigrationStatus();
        
        // If we see the "already exists" message, set isLatest to true
        if (result.message && result.message.includes('already exist')) {
          isLatest = true;
        }
      } else {
        errorMessage = result.message || 'Failed to initialize database.';
      }
    } catch (error: any) {
      errorMessage = `Failed to initialize database: ${error.message}`;
    } finally {
      initDbLoading = false;
    }
  }
</script>

<div class="container mx-auto px-4 py-6">
  <h2 class="text-2xl font-bold mb-6">Database Configuration</h2>
  
  {#if errorMessage}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
      <span class="font-bold">Error:</span>
      <span class="block sm:inline">{errorMessage}</span>
    </div>
  {/if}
  
  {#if successMessage}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" role="alert">
      <span class="font-bold">Success:</span>
      <span class="block sm:inline">{successMessage}</span>
    </div>
  {/if}
  
  <!-- Database settings form -->
  <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
    <div class="mb-6">
      <label class="block text-gray-700 mb-2" for="db-type">
        Database Type
      </label>
      <select
        id="db-type"
        bind:value={dbType}
        on:change={updateConfigModified}
        class="w-full p-2 border border-gray-300 rounded"
        disabled={loading}
      >
        <option value={DatabaseType.SQLITE}>SQLite (File-based)</option>
        <option value={DatabaseType.POSTGRESQL}>PostgreSQL</option>
        <option value={DatabaseType.MYSQL}>MySQL</option>
      </select>
    </div>
    
    {#if dbType === DatabaseType.SQLITE}
      <div class="mb-6">
        <label class="block text-gray-700 mb-2" for="db-path">
          Database File Path
        </label>
        <input
          id="db-path"
          type="text"
          bind:value={dbPath}
          on:input={updateConfigModified}
          class="w-full p-2 border border-gray-300 rounded"
          placeholder="./quicktara.db"
          disabled={loading}
        />
        <p class="text-gray-600 text-sm mt-1">
          Relative to application root or absolute path
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label class="block text-gray-700 mb-2" for="db-host">
            Host
          </label>
          <input
            id="db-host"
            type="text"
            bind:value={dbHost}
            on:input={updateConfigModified}
            class="w-full p-2 border border-gray-300 rounded"
            placeholder="localhost"
            disabled={loading}
          />
        </div>
        <div>
          <label class="block text-gray-700 mb-2" for="db-port">
            Port
          </label>
          <input
            id="db-port"
            type="number"
            bind:value={dbPort}
            on:input={updateConfigModified}
            class="w-full p-2 border border-gray-300 rounded"
            placeholder={dbType === DatabaseType.POSTGRESQL ? "5432" : "3306"}
            disabled={loading}
          />
        </div>
      </div>
      
      <div class="mb-6">
        <label class="block text-gray-700 mb-2" for="db-name">
          Database Name
        </label>
        <input
          id="db-name"
          type="text"
          bind:value={dbName}
          on:input={updateConfigModified}
          class="w-full p-2 border border-gray-300 rounded"
          placeholder="quicktara"
          disabled={loading}
        />
      </div>
      
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label class="block text-gray-700 mb-2" for="db-user">
            Username
          </label>
          <input
            id="db-user"
            type="text"
            bind:value={dbUser}
            on:input={updateConfigModified}
            class="w-full p-2 border border-gray-300 rounded"
            placeholder={dbType === DatabaseType.POSTGRESQL ? "postgres" : "root"}
            disabled={loading}
          />
        </div>
        <div>
          <label class="block text-gray-700 mb-2" for="db-password">
            Password
          </label>
          <input
            id="db-password"
            type="password"
            bind:value={dbPassword}
            on:input={updateConfigModified}
            class="w-full p-2 border border-gray-300 rounded"
            disabled={loading}
          />
        </div>
      </div>
    {/if}
    
    <div class="flex justify-between">
      <button
        on:click={testConnection}
        class="bg-blue-100 hover:bg-blue-200 text-blue-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        disabled={testingConnection}
      >
        {#if testingConnection}
          Testing...
        {:else}
          Test Connection
        {/if}
      </button>
      
      <button
        on:click={saveConfig}
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline {!configModified ? 'opacity-50 cursor-not-allowed' : ''}"  
        disabled={loading || !configModified}
      >
        {#if loading}
          Saving...
        {:else}
          Save Configuration
        {/if}
      </button>
    </div>
  </div>
  
  <!-- Migration status and actions -->
  <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
    <h3 class="text-xl font-semibold mb-4">Database Migration Status</h3>
    
    {#if loading}
      <p>Loading migration status...</p>
    {:else}
      <div class="mb-4">
        <p class="mb-2">
          <span class="font-semibold">Current Revision:</span>
          {currentRevision || 'Not initialized'}
        </p>
        
        <p class="mb-2">
          <span class="font-semibold">Latest Available Revision:</span>
          {latestRevision || 'Not available'}
        </p>
        
        <p class="mb-4">
          <span class="font-semibold">Status:</span>
          {#if isLatest}
            <span class="text-green-600">Up to date</span>
          {:else}
            <span class="text-amber-600">Updates available</span>
          {/if}
        </p>
        
        {#if pendingMigrations.length > 0}
          <div class="mb-4">
            <p class="font-semibold">Pending Migrations:</p>
            <ul class="list-disc list-inside text-gray-700">
              {#each pendingMigrations as migration}
                <li>{migration}</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
      
      <div class="flex space-x-4">
        <button
          on:click={runMigrations}
          class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          disabled={migrationLoading || isLatest || currentRevision === 'Not initialized'}
        >
          {#if migrationLoading}
            Running...
          {:else}
            Run Migrations
          {/if}
        </button>
        
        <button
          on:click={initializeDatabase}
          class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          disabled={initDbLoading}
        >
          {#if initDbLoading}
            Initializing...
          {:else}
            Initialize Database
          {/if}
        </button>
      </div>
    {/if}
  </div>
</div>
