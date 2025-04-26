<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getRiskFrameworks, 
    getActiveRiskFramework,
    setRiskFrameworkActive,
    deleteRiskFramework,
    type RiskFramework
  } from '../../api/risk';
  import RiskMatrixVisualization from './RiskMatrixVisualization.svelte';
  import RiskFrameworkForm from './RiskFrameworkForm.svelte';
  
  // State variables
  let frameworks: RiskFramework[] = [];
  let activeFramework: RiskFramework | null = null;
  let isLoading = true;
  let error = '';
  let showForm = false;
  let showDeleteConfirm = false;
  let frameworkToDelete: RiskFramework | null = null;
  let editingFramework: RiskFramework | null = null;
  let isDeleting = false;
  
  // Load risk frameworks on mount
  onMount(async () => {
    await loadFrameworks();
  });
  
  // Load frameworks from API
  async function loadFrameworks() {
    isLoading = true;
    error = '';
    
    try {
      // Get all frameworks
      const response = await getRiskFrameworks();
      frameworks = response.frameworks;
      
      // Get active framework if exists
      try {
        activeFramework = await getActiveRiskFramework();
      } catch (e: any) {
        console.log('No active framework found');
        activeFramework = null;
      }
      
      isLoading = false;
    } catch (e: any) {
      isLoading = false;
      error = e.message || 'Failed to load risk frameworks';
      console.error('Error loading risk frameworks:', e);
    }
  }
  
  // Set a framework as active
  async function setFrameworkActive(framework: RiskFramework) {
    try {
      await setRiskFrameworkActive(framework.framework_id);
      activeFramework = framework;
      await loadFrameworks(); // Reload to update all frameworks
    } catch (e: any) {
      error = e.message || 'Failed to set framework as active';
      console.error('Error setting framework as active:', e);
    }
  }
  
  // Open form to create a new framework
  function createNewFramework() {
    editingFramework = null;
    showForm = true;
  }
  
  // Open form to edit an existing framework
  function editFramework(framework: RiskFramework) {
    editingFramework = framework;
    showForm = true;
  }
  
  // Handle form completion (success or cancel)
  function handleFormComplete(event: CustomEvent) {
    const { success } = event.detail;
    showForm = false;
    
    if (success) {
      loadFrameworks();
    }
  }
  
  // Show delete confirmation
  function confirmDelete(framework: RiskFramework) {
    frameworkToDelete = framework;
    showDeleteConfirm = true;
  }
  
  // Handle delete confirmation
  async function handleDeleteConfirm() {
    if (!frameworkToDelete) return;
    
    try {
      isDeleting = true;
      error = '';
      
      await deleteRiskFramework(frameworkToDelete.framework_id);
      showDeleteConfirm = false;
      frameworkToDelete = null;
      await loadFrameworks();
    } catch (e: any) {
      error = e.message || `Failed to delete framework: ${frameworkToDelete?.name || 'unknown'}`;
      console.error('Error deleting framework:', e);
    } finally {
      isDeleting = false;
    }
  }
  
  // Cancel delete
  function cancelDelete() {
    showDeleteConfirm = false;
    frameworkToDelete = null;
  }
</script>

<div class="risk-framework-manager">
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold">Risk Calculation Frameworks</h2>
    <button 
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      on:click={createNewFramework}
    >
      New Framework
    </button>
  </div>
  
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <p>{error}</p>
    </div>
  {/if}
  
  {#if isLoading}
    <div class="flex justify-center my-8">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else if frameworks.length === 0}
    <div class="bg-yellow-50 border border-yellow-200 rounded-md p-6 mt-4 text-center">
      <h3 class="text-lg font-medium text-yellow-800 mb-2">No Risk Frameworks Defined</h3>
      <p class="text-yellow-700 mb-4">Define a risk framework to standardize how risk is calculated across your threat analyses.</p>
      <button 
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        on:click={createNewFramework}
      >
        Create First Framework
      </button>
    </div>
  {:else}
    <!-- List of existing frameworks -->
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each frameworks as framework}
        <div class="border rounded-lg shadow-sm overflow-hidden" style="background-color: var(--color-card-bg); border-color: var(--color-border);">
          <div class="p-4 border-b" style="border-color: var(--color-border);">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold">{framework.name}</h3>
                <p class="text-sm text-gray-500">v{framework.version}</p>
              </div>
              {#if framework.is_active}
                <span class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
              {/if}
            </div>
            {#if framework.description}
              <p class="mt-2 text-sm">{framework.description}</p>
            {/if}
          </div>
          
          <!-- Preview of the risk matrix -->
          <div class="p-4 border-b" style="border-color: var(--color-border);">
            <RiskMatrixVisualization 
              riskMatrix={framework.risk_matrix} 
              title="" 
              showLabels={false}
            />
          </div>
          
          <!-- Actions -->
          <div class="p-4 flex justify-between items-center">
            <span class="text-xs text-gray-500">Created: {new Date(framework.created_at).toLocaleDateString()}</span>
            <div class="space-x-2">
              {#if !framework.is_active}
                <button 
                  class="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                  on:click={() => setFrameworkActive(framework)}
                >
                  Set Active
                </button>
              {/if}
              <button 
                class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                on:click={() => editFramework(framework)}
              >
                Edit
              </button>
              <button 
                class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                on:click={() => confirmDelete(framework)}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Modal form for creating/editing frameworks -->
  {#if showForm}
    <div class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-4xl max-h-screen overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">
              {editingFramework ? 'Edit Risk Framework' : 'Create Risk Framework'}
            </h2>
            <button 
              class="text-gray-500 hover:text-gray-700"
              on:click={() => showForm = false}
              aria-label="Close form"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <RiskFrameworkForm 
            framework={editingFramework} 
            on:complete={handleFormComplete}
          />
        </div>
      </div>
    </div>
  {/if}

  <!-- Delete confirmation modal -->
  {#if showDeleteConfirm && frameworkToDelete}
    <div class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 class="text-xl font-semibold mb-4">Confirm Deletion</h2>
        <p class="mb-6">Are you sure you want to delete the framework <strong>{frameworkToDelete.name}</strong>?</p>
        
        {#if frameworkToDelete.is_active}
          <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
            <p class="text-yellow-700">
              <strong>Warning:</strong> This is currently the active framework. Deleting it may affect risk calculations.
            </p>
          </div>
        {/if}
        
        <div class="flex justify-end space-x-3">
          <button 
            class="px-4 py-2 border rounded-md" 
            style="border-color: var(--color-border);"
            on:click={cancelDelete}
            disabled={isDeleting}
          >
            Cancel
          </button>
          <button 
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            on:click={handleDeleteConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
