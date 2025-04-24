<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Upload, Download, RefreshCw, AlertCircle } from '@lucide/svelte';
  import ComponentCard from './ComponentCard.svelte';
  import ComponentFilter from './ComponentFilter.svelte';
  import ComponentForm from './ComponentForm.svelte';
  import ComponentImport from './ComponentImport.svelte';
  import { componentApi } from '../api/components';
  import { safeApiCall } from '../utils/error-handler';
  
  // Component management state
  let components: any[] = [];
  let filteredComponents: any[] = [];
  let isLoading = true;
  let error = '';
  let showForm = false;
  let editingComponent: any = null;
  let showImportModal = false;
  
  // Filter state
  let filters = {
    searchTerm: '',
    type: '',
    safetyLevel: '',
    trustZone: ''
  };
  
  onMount(async () => {
    await loadComponents();
  });
  
  async function loadComponents() {
    isLoading = true;
    error = '';
    
    try {
      const result = await componentApi.getAll();
      
      // The API should now return an array (potentially empty)
      components = Array.isArray(result) ? result : [];
      applyFilters();
    } catch (err) {
      console.error('Error loading components:', err);
      error = 'Failed to load components. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  function applyFilters(newFilters: any = null) {
    if (newFilters) {
      filters = newFilters;
    }
    
    filteredComponents = components.filter(component => {
      // Search term filter (case insensitive)
      const searchTermMatch = !filters.searchTerm || 
        component.name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        component.component_id.toLowerCase().includes(filters.searchTerm.toLowerCase());
      
      // Type filter
      const typeMatch = !filters.type || component.type === filters.type;
      
      // Safety level filter
      const safetyLevelMatch = !filters.safetyLevel || component.safety_level === filters.safetyLevel;
      
      // Trust zone filter
      const trustZoneMatch = !filters.trustZone || component.trust_zone === filters.trustZone;
      
      return searchTermMatch && typeMatch && safetyLevelMatch && trustZoneMatch;
    });
  }
  
  function handleFilter(event: CustomEvent) {
    applyFilters(event.detail);
  }
  
  export function handleAddComponent() {
    editingComponent = null;
    showForm = true;
  }
  
  function handleEditComponent(component: any) {
    editingComponent = { ...component };
    showForm = true;
  }
  
  async function handleDeleteComponent(componentId: string) {
    if (confirm(`Are you sure you want to delete this component: ${componentId}?`)) {
      const success = await safeApiCall(() => componentApi.delete(componentId));
      
      if (success) {
        components = components.filter(c => c.component_id !== componentId);
        applyFilters();
      }
    }
  }
  
  async function handleFormSubmit(event: CustomEvent) {
    const componentData = event.detail;
    
    if (editingComponent) {
      // Update existing component
      const updatedComponent = await safeApiCall(() => 
        componentApi.update(componentData.component_id, componentData)
      );
      
      if (updatedComponent) {
        components = components.map(c => 
          c.component_id === updatedComponent.component_id ? updatedComponent : c
        );
        showForm = false;
      }
    } else {
      // Create new component
      const newComponent = await safeApiCall(() => 
        componentApi.create(componentData)
      );
      
      if (newComponent) {
        components = [...components, newComponent];
        showForm = false;
      }
    }
    
    applyFilters();
  }
  
  function handleFormCancel() {
    showForm = false;
    editingComponent = null;
  }
  
  export function handleOpenImport() {
    showImportModal = true;
  }
  
  function handleImportClose() {
    showImportModal = false;
  }
  
  async function handleImportSuccess(event: CustomEvent) {
    const importedComponents = event.detail;
    await loadComponents(); // Reload all components to ensure we have the latest data
  }
  
  export function handleExportCSV() {
    window.open(componentApi.getExportUrl(), '_blank');
  }
</script>

<div>
  <!-- Filter Component -->
  <ComponentFilter on:filter={handleFilter} />
  
  <!-- Component List -->
  <div>
    {#if isLoading}
      <div class="flex justify-center items-center h-64">
        <div class="text-center">
          <RefreshCw size={36} class="animate-spin mx-auto text-primary mb-4" />
          <p class="text-gray-600">Loading components...</p>
        </div>
      </div>
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 flex items-start">
        <AlertCircle size={20} class="mr-3 mt-0.5 flex-shrink-0" />
        <div>
          <h3 class="font-medium">Error loading components</h3>
          <p class="mt-1">{error}</p>
          <button 
            on:click={loadComponents}
            class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 flex items-center gap-1">
            <RefreshCw size={14} /> Try again
          </button>
        </div>
      </div>
    {:else if filteredComponents.length === 0}
      <div class="bg-gray-50 border border-gray-200 text-gray-600 rounded-lg p-8 text-center">
        {#if components.length === 0}
          <p class="mb-4">No components found. Add your first component to get started.</p>
          <button 
            on:click={handleAddComponent}
            class="btn btn-primary inline-flex items-center gap-1">
            <Plus size={16} />
            <span>Add Component</span>
          </button>
        {:else}
          <p>No components match your filters.</p>
          <button 
            on:click={() => applyFilters({ searchTerm: '', type: '', safetyLevel: '', trustZone: '' })}
            class="btn px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 mt-2">
            Clear Filters
          </button>
        {/if}
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each filteredComponents as component (component.component_id)}
          <ComponentCard 
            {component}
            on:edit={() => handleEditComponent(component)}
            on:delete={() => handleDeleteComponent(component.component_id)} 
          />
        {/each}
      </div>
      
      {#if filteredComponents.length !== components.length}
        <p class="text-sm text-gray-500 mt-4">
          Showing {filteredComponents.length} of {components.length} components
        </p>
      {/if}
    {/if}
  </div>
  
  <!-- Component Form Dialog (only shown when showForm is true) -->
  {#if showForm}
    <!-- Improved modal backdrop with blur effect and warmer overlay -->
    <div class="fixed inset-0 backdrop-blur-sm bg-neutral-900/40 flex items-center justify-center z-50 p-4 transition-opacity duration-200">
      <div class="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <ComponentForm 
          editMode={!!editingComponent}
          component={editingComponent || undefined}
          availableComponents={components}
          on:submit={handleFormSubmit}
          on:cancel={handleFormCancel}
        />
      </div>
    </div>
  {/if}
  
  <!-- Import Modal -->
  <ComponentImport 
    isOpen={showImportModal}
    on:close={handleImportClose}
    on:import={handleImportSuccess}
  />
</div>
