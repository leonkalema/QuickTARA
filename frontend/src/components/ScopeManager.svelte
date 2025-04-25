<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, AlertCircle, Plus, Target, Database } from '@lucide/svelte';
  import ScopeList from './ScopeList.svelte';
  import ScopeForm from './ScopeForm.svelte';
  import { scopeApi, SystemType } from '../api/scope';
  import { safeApiCall } from '../utils/error-handler';
  
  // Component references
  let scopeListInstance: any;
  
  // Summary stats
  let stats = {
    totalScopes: 0,
    byType: {
      [SystemType.SUBSYSTEM]: 0,
      [SystemType.API]: 0,
      [SystemType.BACKEND]: 0,
      [SystemType.FULLSYSTEM]: 0,
      [SystemType.EMBEDDED]: 0,
      [SystemType.OTHER]: 0
    }
  };
  
  // UI state
  let isLoading = false;
  let showForm = false;
  let editingScope: any = null;
  let viewMode = false;
  
  function updateStats(scopes: any[]) {
    stats.totalScopes = scopes.length;
    
    // Reset counts
    Object.keys(stats.byType).forEach(key => {
      stats.byType[key as keyof typeof stats.byType] = 0;
    });
    
    // Count by type
    scopes.forEach(scope => {
      if (scope.system_type in stats.byType) {
        stats.byType[scope.system_type as keyof typeof stats.byType]++;
      }
    });
  }
  
  // Load scopes on mount
  onMount(async () => {
    await loadScopes();
  });
  
  // Load scopes from API
  async function loadScopes() {
    isLoading = true;
    const result = await safeApiCall(scopeApi.getAll);
    if (result) {
      updateStats(result.scopes);
    }
    isLoading = false;
  }
  
  function handleScopesUpdate(scopes: any[]) {
    updateStats(scopes);
  }
  
  function handleAddScope() {
    editingScope = null;
    viewMode = false;
    showForm = true;
  }
</script>

<div>
  <!-- Stats cards area -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
    <div class="metric-card">
      <div class="flex items-start">
        <Target size={24} style="color: var(--color-primary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Total System Scopes</p>
          <p class="metric-value">{stats.totalScopes}</p>
        </div>
      </div>
    </div>
    
    <div class="metric-card">
      <div class="flex items-start">
        <Database size={24} style="color: var(--color-secondary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Full Systems</p>
          <p class="metric-value">{stats.byType[SystemType.FULLSYSTEM]}</p>
        </div>
      </div>
    </div>
    
    <div class="metric-card">
      <div class="flex items-start">
        <svg class="w-6 h-6 mr-3 mt-1" style="color: var(--color-success);" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
        </svg>
        <div>
          <p class="metric-label">Embedded Systems</p>
          <p class="metric-value">{stats.byType[SystemType.EMBEDDED]}</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">System Scopes</h2>
    <div class="flex space-x-2">
      <button 
        on:click={loadScopes}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);" 
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
        <RefreshCw size={16} class="{isLoading ? 'animate-spin' : ''}" />
        <span class="sr-only md:not-sr-only">Refresh</span>
      </button>
      
      <button 
        on:click={handleAddScope}
        class="btn btn-primary flex items-center gap-1">
        <Plus size={16} />
        <span>Add Scope</span>
      </button>
    </div>
  </div>
  
  <!-- Scope List Component -->
  <ScopeList 
    bind:this={scopeListInstance} 
    on:update={(e: CustomEvent<any[]>) => handleScopesUpdate(e.detail)}
    on:view={(e: CustomEvent<any>) => {
      // Set the scope for viewing and show the form in view mode
      editingScope = e.detail;
      viewMode = true;
      showForm = true;
    }} />
  
  <!-- Form Dialog (shown when showForm is true) -->
  {#if showForm}
    <div class="fixed inset-0 backdrop-blur-sm bg-neutral-900/40 flex items-center justify-center z-50 p-4 transition-opacity duration-200">
      <div class="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <ScopeForm 
          editMode={!!editingScope && !viewMode}
          viewMode={viewMode}
          scope={editingScope || undefined}
          on:submit={async (e: CustomEvent<any>) => {
            if (editingScope) {
              await safeApiCall(() => scopeApi.update(editingScope.scope_id, e.detail));
            } else {
              await safeApiCall(() => scopeApi.create(e.detail));
            }
            showForm = false;
            viewMode = false;
            loadScopes();
          }}
          on:switchToEdit={() => {
            viewMode = false; // Switch to edit mode
          }}
          on:cancel={(e: CustomEvent<any>) => {
            showForm = false;
            viewMode = false;
            editingScope = null;
          }}
        />
      </div>
    </div>
  {/if}
</div>

<style>
  .metric-card {
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-card-bg);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  
  .metric-label {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    margin-bottom: 0.25rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-main);
  }
</style>
