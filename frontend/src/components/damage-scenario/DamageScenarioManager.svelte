<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, RefreshCw, AlertTriangle, Shield, Activity, Trash2, ListPlus } from '@lucide/svelte';
  import { damageScenarioApi, type DamageScenario, DamageCategory, SeverityLevel } from '../../api/damage-scenarios';
  import { scopeApi, type Scope } from '../../api/scopes';
  import { componentApi, type Component } from '../../api/components';
  import { safeApiCall } from '../../utils/error-handler';
  import { showSuccess, showError } from '../ToastManager.svelte';
  import DamageScenarioListComponent from './DamageScenarioList.svelte';
  import DamageScenarioForm from './DamageScenarioForm.svelte';
  import DamageScenarioBatchCreator from './DamageScenarioBatchCreator.svelte';
  
  // Props
  export let scopeId: string | null = null;
  export let componentId: string | null = null;
  
  // State
  let scenarios: DamageScenario[] = [];
  let totalScenarios: number = 0;
  let isLoading = true;
  let error = '';
  let showForm = false;
  let showBatchCreator = false;
  let showViewPanel = false;
  let showDeleteModal = false;
  let editingScenario: DamageScenario | null = null;
  let viewingScenario: DamageScenario | null = null;
  let scenarioToDelete: DamageScenario | null = null;
  
  // Data for filters
  let availableScopes: Scope[] = [];
  let availableComponents: Component[] = [];
  let isLoadingFilterData = false;
  
  // Pagination
  let currentPage = 1;
  let pageSize = 10;
  
  // Filters
  let selectedScopeId = scopeId;
  let selectedComponentId = componentId;
  let selectedDamageCategory: string | null = null;
  let selectedSeverity: string | null = null;
  
  // Stats
  let stats = {
    totalScenarios: 0,
    criticalScenarios: 0,
    highScenarios: 0,
    directImpacts: 0,
    cascadingImpacts: 0
  };
  
  onMount(async () => {
    // Load filter data and damage scenarios in parallel
    await Promise.all([
      loadFilterData(),
      loadDamageScenarios()
    ]);
  });
  
  /**
   * Load scopes and components for filters
   */
  async function loadFilterData() {
    isLoadingFilterData = true;
    
    try {
      // Load scopes and components in parallel
      const [scopesResult, componentsResult] = await Promise.all([
        safeApiCall(() => scopeApi.getAll()),
        safeApiCall(() => componentApi.getAll())
      ]);
      
      if (scopesResult) {
        availableScopes = scopesResult.scopes || [];
      }
      
      if (componentsResult) {
        availableComponents = Array.isArray(componentsResult) ? componentsResult : [];
      }
    } catch (err) {
      console.error('Error loading filter data:', err);
      // Don't show error for filter data loading, as it's not critical
    } finally {
      isLoadingFilterData = false;
    }
  };
  
  async function loadDamageScenarios() {
    isLoading = true;
    error = '';
    
    try {
      const skip = (currentPage - 1) * pageSize;
      
      const result = await safeApiCall(() => damageScenarioApi.getAll({
        skip,
        limit: pageSize,
        scope_id: selectedScopeId || undefined,
        component_id: selectedComponentId || undefined,
        damage_category: selectedDamageCategory || undefined,
        severity: selectedSeverity || undefined
      }));
      
      if (result) {
        scenarios = result.scenarios;
        totalScenarios = result.total;
        updateStats(scenarios);
      }
    } catch (err) {
      console.error('Error loading damage scenarios:', err);
      error = 'Failed to load damage scenarios. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  function updateStats(scenarios: DamageScenario[]) {
    stats.totalScenarios = totalScenarios;
    stats.criticalScenarios = scenarios.filter(s => s.severity === 'Critical').length;
    stats.highScenarios = scenarios.filter(s => s.severity === 'High').length;
    stats.directImpacts = scenarios.filter(s => s.impact_type === 'Direct').length;
    stats.cascadingImpacts = scenarios.filter(s => s.impact_type === 'Cascading').length;
  }
  
  /**
   * Get component name by ID
   */
  function getComponentName(componentId: string): string {
    const component = availableComponents.find(c => c.component_id === componentId);
    return component ? component.name : 'Unknown Component';
  }
  
  function handleCreateScenario() {
    showForm = true;
    showBatchCreator = false;
    editingScenario = null;
  }

  function handleBatchCreateScenario() {
    showBatchCreator = true;
    showForm = false;
  }
  
  function handleEditScenario(scenario: DamageScenario) {
    editingScenario = scenario;
    showForm = true;
  }
  
  function handleViewScenario(scenario: DamageScenario) {
    viewingScenario = scenario;
    showViewPanel = true;
  }
  
  function handleCloseViewPanel() {
    showViewPanel = false;
    viewingScenario = null;
  }
  
  function showDeleteConfirmation(scenario: DamageScenario) {
    scenarioToDelete = scenario;
    showDeleteModal = true;
  }
  
  function cancelDelete() {
    showDeleteModal = false;
    scenarioToDelete = null;
  }
  
  async function confirmDelete() {
    if (!scenarioToDelete) return;
    
    try {
      await handleDeleteScenario(scenarioToDelete);
      showDeleteModal = false;
      scenarioToDelete = null;
    } catch (err) {
      console.error('Error deleting scenario:', err);
    }
  }
  
  function handleFormCancel() {
    showForm = false;
    showBatchCreator = false;
    editingScenario = null;
  }
  
  async function handleFormSubmit(event: CustomEvent) {
    const scenarioData = event.detail;
    
    try {
      if (editingScenario) {
        // Update existing scenario
        const updatedScenario = await safeApiCall(() => 
          damageScenarioApi.update(editingScenario!.scenario_id, scenarioData)
        );
        
        if (updatedScenario) {
          // Update the scenario in the list
          scenarios = scenarios.map(s => 
            s.scenario_id === updatedScenario.scenario_id ? updatedScenario : s
          );
          
          showSuccess(`Damage scenario "${updatedScenario.name}" updated successfully`);
        }
      } else {
        // Create new scenario
        const newScenario = await safeApiCall(() => 
          damageScenarioApi.create(scenarioData)
        );
        
        if (newScenario) {
          // Add the new scenario to the list if it matches current filters
          let matchesFilters = true;
          
          if (selectedScopeId && newScenario.scope_id !== selectedScopeId) {
            matchesFilters = false;
          }
          
          if (selectedComponentId && 
              newScenario.primary_component_id !== selectedComponentId && 
              !newScenario.affected_component_ids.includes(selectedComponentId)) {
            matchesFilters = false;
          }
          
          if (selectedDamageCategory && newScenario.damage_category !== selectedDamageCategory) {
            matchesFilters = false;
          }
          
          if (selectedSeverity && newScenario.severity !== selectedSeverity) {
            matchesFilters = false;
          }
          
          if (matchesFilters) {
            scenarios = [newScenario, ...scenarios];
            totalScenarios += 1;
          } else {
            // If it doesn't match current filters, reload to update counts
            await loadDamageScenarios();
          }
          
          showSuccess(`Damage scenario "${newScenario.name}" created successfully`);
        }
      }
      
      showForm = false;
      editingScenario = null;
      updateStats(scenarios);
    } catch (err) {
      console.error('Error saving damage scenario:', err);
      showError('Failed to save damage scenario. Please try again.');
    }
  }
  
  async function handleDeleteScenario(scenario: DamageScenario) {
    isLoading = true;
    
    try {
      await safeApiCall(() => damageScenarioApi.delete(scenario.scenario_id));
      showSuccess(`Damage scenario "${scenario.name}" deleted successfully`);
      await loadDamageScenarios();
    } catch (err) {
      console.error('Error deleting scenario:', err);
      showError('Failed to delete damage scenario. Please try again.');
    } finally {
      isLoading = false;
    }
  }
  
  function handlePageChange(page: number) {
    currentPage = page;
    loadDamageScenarios();
  }
  
  function handleFilterChange() {
    currentPage = 1; // Reset to first page when filters change
    loadDamageScenarios();
  }
</script>

<div class="space-y-6">
  <!-- Stats cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
    <!-- Total Scenarios -->
    <div class="metric-card">
      <div class="flex items-start">
        <Shield size={24} style="color: var(--color-primary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Total Scenarios</p>
          <p class="metric-value">{stats.totalScenarios}</p>
        </div>
      </div>
    </div>
    
    <!-- Critical Scenarios -->
    <div class="metric-card">
      <div class="flex items-start">
        <AlertTriangle size={24} style="color: var(--color-danger);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Critical Scenarios</p>
          <p class="metric-value">{stats.criticalScenarios}</p>
        </div>
      </div>
    </div>
    
    <!-- High Scenarios -->
    <div class="metric-card">
      <div class="flex items-start">
        <AlertTriangle size={24} style="color: var(--color-warning);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">High Scenarios</p>
          <p class="metric-value">{stats.highScenarios}</p>
        </div>
      </div>
    </div>
    
    <!-- Direct Impacts -->
    <div class="metric-card">
      <div class="flex items-start">
        <Activity size={24} style="color: var(--color-info);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Direct Impacts</p>
          <p class="metric-value">{stats.directImpacts}</p>
        </div>
      </div>
    </div>
    
    <!-- Cascading Impacts -->
    <div class="metric-card">
      <div class="flex items-start">
        <Activity size={24} style="color: var(--color-success);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Cascading Impacts</p>
          <p class="metric-value">{stats.cascadingImpacts}</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">Damage Scenarios</h2>
    
    <div class="flex space-x-2">
      <button 
        on:click={handleCreateScenario}
        class="btn btn-primary flex items-center gap-1 mr-2"
      >
        <Plus size={18} />
        Create Single Scenario
      </button>

      <button 
        on:click={handleBatchCreateScenario}
        class="btn btn-primary flex items-center gap-1 mr-2"
      >
        <ListPlus size={18} />
        Batch Create Scenarios
      </button>
      
      <button 
        on:click={loadDamageScenarios}
        class="btn btn-secondary flex items-center gap-1"
        disabled={isLoading}
      >
        <RefreshCw size={18} class={isLoading ? 'animate-spin' : ''} />
        Refresh
      </button>
    </div>
  </div>
  
  <!-- Batch Creator Modal -->
  {#if showBatchCreator}
    <DamageScenarioBatchCreator
      on:cancel={handleFormCancel}
      on:complete={() => {
        showBatchCreator = false;
        loadDamageScenarios();
      }}
    />
  {/if}
  
  <!-- Filters -->
  <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Scope Filter -->
      {#if !scopeId}
        <div>
          <label for="scope-filter" class="block text-sm font-medium text-gray-700 mb-1">Scope</label>
          <select 
            id="scope-filter" 
            class="form-select w-full rounded-md border-gray-300"
            bind:value={selectedScopeId}
            on:change={handleFilterChange}
          >
            <option value={null}>All Scopes</option>
            {#each availableScopes as scope}
              <option value={scope.scope_id}>{scope.name}</option>
            {/each}
          </select>
        </div>
      {/if}
      
      <!-- Component Filter -->
      {#if !componentId}
        <div>
          <label for="component-filter" class="block text-sm font-medium text-gray-700 mb-1">Component</label>
          <select 
            id="component-filter" 
            class="form-select w-full rounded-md border-gray-300"
            bind:value={selectedComponentId}
            on:change={handleFilterChange}
          >
            <option value={null}>All Components</option>
            {#each availableComponents as component}
              <option value={component.component_id}>{component.name}</option>
            {/each}
          </select>
        </div>
      {/if}
      
      <!-- Damage Category Filter -->
      <div>
        <label for="category-filter" class="block text-sm font-medium text-gray-700 mb-1">Damage Category</label>
        <select 
          id="category-filter" 
          class="form-select w-full rounded-md border-gray-300"
          bind:value={selectedDamageCategory}
          on:change={handleFilterChange}
        >
          <option value={null}>All Categories</option>
          {#each Object.values(DamageCategory) as category}
            <option value={category}>{category}</option>
          {/each}
        </select>
      </div>
      
      <!-- Severity Filter -->
      <div>
        <label for="severity-filter" class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
        <select 
          id="severity-filter" 
          class="form-select w-full rounded-md border-gray-300"
          bind:value={selectedSeverity}
          on:change={handleFilterChange}
        >
          <option value={null}>All Severities</option>
          {#each Object.values(SeverityLevel) as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
  
  <!-- Damage Scenario List -->
  <DamageScenarioListComponent 
    scenarios={scenarios}
    totalScenarios={totalScenarios}
    currentPage={currentPage}
    pageSize={pageSize}
    isLoading={isLoading}
    error={error}
    on:edit={(e: CustomEvent<DamageScenario>) => handleEditScenario(e.detail)}
    on:delete={(e: CustomEvent<DamageScenario>) => showDeleteConfirmation(e.detail)}
    on:view={(e: CustomEvent<DamageScenario>) => handleViewScenario(e.detail)}
    on:pageChange={(e: CustomEvent<number>) => handlePageChange(e.detail)}
  />
  
  <!-- Create/Edit Form Modal -->
  {#if showForm}
    <DamageScenarioForm 
      scenario={editingScenario}
      scopeId={selectedScopeId}
      componentId={selectedComponentId}
      on:cancel={handleFormCancel}
      on:submit={handleFormSubmit}
    />
  {/if}
  
  <!-- Damage Scenario View Panel -->
  {#if showViewPanel && viewingScenario}
    <!-- Semi-transparent backdrop with accessibility attributes -->
    <div 
      class="fixed inset-0 bg-neutral-900/40 z-40 transition-opacity duration-200" 
      on:click={handleCloseViewPanel}
      on:keydown={(e) => e.key === 'Escape' && handleCloseViewPanel()}
      role="button"
      tabindex="0"
      aria-label="Close panel"
    ></div>
    
    <!-- Slide-in panel from the right -->
    <div class="fixed inset-y-0 right-0 w-full md:w-2/3 lg:w-1/2 xl:w-2/5 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out overflow-auto" 
         style="border-left: 1px solid var(--color-border);">
      <div class="h-full overflow-y-auto">
        <!-- Component View Template - Cleaner and more concise -->
        <div class="p-6 h-full flex flex-col">
          <div class="flex justify-between items-center mb-6 border-b pb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900">Damage Scenario Details</h2>
              <p class="text-sm text-gray-500 mt-1">{viewingScenario.scenario_id}</p>
            </div>
            <button 
              on:click={handleCloseViewPanel}
              class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Close panel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="overflow-y-auto flex-grow space-y-6">
            <!-- Basic Information -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Basic Information</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p class="text-sm font-medium text-gray-500">Name</p>
                  <p class="text-base">{viewingScenario.name}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Severity</p>
                  <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    {viewingScenario.severity === 'Critical' ? 'bg-red-100 text-red-800' : 
                     viewingScenario.severity === 'High' ? 'bg-orange-100 text-orange-800' : 
                     viewingScenario.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
                     'bg-green-100 text-green-800'}"
                  >
                    {viewingScenario.severity}
                  </p>
                </div>
              </div>
              
              <div class="mt-4">
                <p class="text-sm font-medium text-gray-500">Description</p>
                <p class="text-base">{viewingScenario.description || 'No description provided.'}</p>
              </div>
            </div>
            
            <!-- Impact Details -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Impact Details</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p class="text-sm font-medium text-gray-500">Damage Category</p>
                  <p class="text-base">{viewingScenario.damage_category}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Impact Type</p>
                  <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    {viewingScenario.impact_type === 'Direct' ? 'bg-blue-100 text-blue-800' : 
                     viewingScenario.impact_type === 'Indirect' ? 'bg-purple-100 text-purple-800' : 
                     'bg-teal-100 text-teal-800'}"
                  >
                    {viewingScenario.impact_type}
                  </p>
                </div>
              </div>
              
              <div class="mt-4">
                <p class="text-sm font-medium text-gray-500">CIA Impact</p>
                <div class="flex space-x-2 mt-1">
                  {#if viewingScenario.confidentiality_impact}
                    <span class="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">Confidentiality</span>
                  {/if}
                  {#if viewingScenario.integrity_impact}
                    <span class="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">Integrity</span>
                  {/if}
                  {#if viewingScenario.availability_impact}
                    <span class="px-2 py-1 text-xs font-semibold rounded bg-purple-100 text-purple-800">Availability</span>
                  {/if}
                </div>
              </div>
            </div>
            
            <!-- Component Information -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Component Information</h3>
              
              <div>
                <p class="text-sm font-medium text-gray-500">Primary Component</p>
                <p class="text-base">{getComponentName(viewingScenario.primary_component_id)}</p>
              </div>
              
              <div class="mt-4">
                <p class="text-sm font-medium text-gray-500">Affected Components</p>
                {#if viewingScenario.affected_component_ids.length > 0}
                  <ul class="list-disc list-inside space-y-1 mt-1">
                    {#each viewingScenario.affected_component_ids as componentId}
                      <li class="text-sm">{getComponentName(componentId)}</li>
                    {/each}
                  </ul>
                {:else}
                  <p class="text-sm text-gray-500">No additional affected components</p>
                {/if}
              </div>
            </div>
            
            <!-- Metadata -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Metadata</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p class="text-sm font-medium text-gray-500">Created At</p>
                  <p class="text-sm">{new Date(viewingScenario.created_at).toLocaleString()}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Last Updated</p>
                  <p class="text-sm">{new Date(viewingScenario.updated_at).toLocaleString()}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Version</p>
                  <p class="text-sm">{viewingScenario.version}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Scenario ID</p>
                  <p class="text-sm font-mono">{viewingScenario.scenario_id}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="mt-4 pt-4 border-t flex justify-end space-x-3">
            <button 
              on:click={() => { 
                handleCloseViewPanel(); 
                if (viewingScenario) {
                  handleEditScenario(viewingScenario);
                }
              }}
              class="btn btn-secondary"
            >
              Edit
            </button>
            <button 
              on:click={handleCloseViewPanel}
              class="btn btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Delete Confirmation Modal -->
  {#if showDeleteModal && scenarioToDelete}
    <div class="fixed inset-0 bg-neutral-900/40 z-50 flex items-center justify-center transition-opacity duration-200">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
        <div class="p-5 border-b border-gray-200">
          <div class="flex items-center">
            <div class="bg-red-100 p-2 rounded-full mr-3">
              <AlertTriangle size={24} class="text-red-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Delete Damage Scenario</h3>
          </div>
        </div>
        
        <div class="p-5">
          <p class="text-gray-700 mb-2">Are you sure you want to delete this damage scenario?</p>
          <p class="font-medium text-gray-900 mb-1">{scenarioToDelete.name}</p>
          <p class="text-sm text-gray-500 mb-4">{scenarioToDelete.scenario_id}</p>
          
          <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <AlertTriangle size={20} class="text-red-600" />
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">
                  This action cannot be undone. This will permanently delete the damage scenario and remove all associated data.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="px-5 py-4 bg-gray-50 flex justify-end space-x-3">
          <button 
            type="button"
            on:click={cancelDelete}
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="button"
            on:click={confirmDelete}
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .metric-card {
    background-color: var(--color-card-bg);
    border: 1px solid var(--color-border);
    padding: 1.25rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  .metric-label {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }
  
  .metric-value {
    color: var(--color-text-main);
    font-size: 1.5rem;
    font-weight: 600;
  }
</style>
