<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Upload, Download, RefreshCw, AlertCircle, X, Edit, Trash2, AlertTriangle } from '@lucide/svelte';
  import { showSuccess, showError, showInfo, showWarning } from './ToastManager.svelte';
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
  let viewingComponent: any = null;
  let showImportModal = false;
  let showDeleteModal = false;
  let componentToDelete: any = null;
  
  // Filter state
  let filters = {
    searchTerm: '',
    type: '',
    safetyLevel: '',
    trustZone: '',
    scope: ''
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
      
      // Scope filter
      const scopeMatch = !filters.scope || component.scope_id === filters.scope;
      
      return searchTermMatch && typeMatch && safetyLevelMatch && trustZoneMatch && scopeMatch;
    });
  }
  
  function handleFilter(event: CustomEvent) {
    applyFilters(event.detail);
  }
  
  export function handleAddComponent() {
    editingComponent = null;
    showForm = true;
  }
  
  function handleViewComponent(component: any) {
    viewingComponent = { ...component };
    editingComponent = null;
    showForm = true;
  }

  function handleEditComponent(component: any) {
    editingComponent = { ...component };
    viewingComponent = null;
    showForm = true;
  }
  
  function showDeleteConfirmation(component: any) {
    componentToDelete = component;
    showDeleteModal = true;
  }
  
  async function confirmDelete() {
    if (!componentToDelete) return;
    
    const componentId = componentToDelete.component_id;
    const componentName = componentToDelete.name;
    const success = await safeApiCall(() => componentApi.delete(componentId));
    
    if (success) {
      components = components.filter(c => c.component_id !== componentId);
      applyFilters();
      showSuccess(`Component "${componentName}" was successfully deleted`);
    } else {
      showError('Failed to delete component');
    }
    
    // Close the modal
    showDeleteModal = false;
    componentToDelete = null;
  }
  
  function cancelDelete() {
    showDeleteModal = false;
    componentToDelete = null;
  }
  
  async function handleFormSubmit(event: CustomEvent) {
    const component = event.detail;
    let success;
    const isNew = !component.component_id;
    
    if (!isNew) {
      // Update existing component
      success = await safeApiCall(() => componentApi.update(component.component_id, component));
      if (success) {
        showSuccess(`Component "${component.name}" was successfully updated`);
      } else {
        showError('Failed to update component');
      }
    } else {
      // Create new component
      success = await safeApiCall(() => componentApi.create(component));
      if (success) {
        showSuccess(`Component "${component.name}" was successfully created`);
      } else {
        showError('Failed to create component');
      }
    }
    
    if (success) {
      // Reload all components to get the updated list
      await loadComponents();
      showForm = false;
      editingComponent = null;
      viewingComponent = null;
    }
    
    applyFilters();
  }
  
  function handleFormCancel() {
    showForm = false;
    editingComponent = null;
    viewingComponent = null;
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
            on:view={() => handleViewComponent(component)}
            on:edit={() => handleEditComponent(component)}
            on:delete={() => showDeleteConfirmation(component)} 
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
  
  <!-- Component Form Slide-in Panel (only shown when showForm is true) -->
  {#if showForm}
    <!-- Semi-transparent backdrop with accessibility attributes -->
    <div 
      class="fixed inset-0 bg-neutral-900/40 z-40 transition-opacity duration-200" 
      on:click={handleFormCancel}
      on:keydown={(e) => e.key === 'Escape' && handleFormCancel()}
      role="button"
      tabindex="0"
      aria-label="Close panel"
    ></div>
    
    <!-- Slide-in panel from the right -->
    <div class="fixed inset-y-0 right-0 w-full md:w-2/3 lg:w-1/2 xl:w-2/5 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out overflow-auto" 
         style="border-left: 1px solid var(--color-border);">
      <div class="h-full overflow-y-auto">
        {#if viewingComponent}
          <!-- Component View Template - Cleaner and more concise -->
          <div class="p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-6 border-b pb-4">
              <div>
                <h2 class="text-xl font-bold text-gray-900">Component Details</h2>
                <p class="text-sm text-gray-500 mt-1">{viewingComponent.component_id}</p>
              </div>
              <button 
                on:click={handleFormCancel}
                class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div class="overflow-y-auto flex-grow">
              <!-- Basic Info Card -->
              <div class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                <h3 class="font-medium text-gray-900 mb-3">Basic Information</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-500">Name</p>
                    <p class="font-medium">{viewingComponent.name}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Type</p>
                    <p class="font-medium">{viewingComponent.type}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Safety Level</p>
                    <p class="font-medium">{viewingComponent.safety_level}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Trust Zone</p>
                    <p class="font-medium">{viewingComponent.trust_zone}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Location</p>
                    <p class="font-medium">{viewingComponent.location}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Scope</p>
                    <p class="font-medium">{viewingComponent.scope_id || 'None'}</p>
                  </div>
                </div>
              </div>
              
              <!-- Security Properties Card -->
              <div class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                <h3 class="font-medium text-gray-900 mb-3">Security Properties</h3>
                <div class="grid grid-cols-3 gap-4 mb-3">
                  <div>
                    <p class="text-sm text-gray-500">Confidentiality</p>
                    <p class="font-medium">{viewingComponent.confidentiality}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Integrity</p>
                    <p class="font-medium">{viewingComponent.integrity}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Availability</p>
                    <p class="font-medium">{viewingComponent.availability}</p>
                  </div>
                </div>
                <div class="flex gap-6">
                  <div class="flex items-center">
                    <input type="checkbox" checked={viewingComponent.authenticity_required} disabled class="mr-2" />
                    <p class="text-sm">Authenticity Required</p>
                  </div>
                  <div class="flex items-center">
                    <input type="checkbox" checked={viewingComponent.authorization_required} disabled class="mr-2" />
                    <p class="text-sm">Authorization Required</p>
                  </div>
                </div>
              </div>
              
              <!-- Interfaces & Connections -->
              <div class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                <h3 class="font-medium text-gray-900 mb-3">Interfaces</h3>
                <div class="flex flex-wrap gap-2 mb-4">
                  {#if viewingComponent.interfaces && viewingComponent.interfaces.length > 0}
                    {#each viewingComponent.interfaces.filter((i: string) => i) as interfaceItem}
                      <span class="px-2 py-1 bg-white border border-gray-200 rounded text-sm">{interfaceItem}</span>
                    {/each}
                  {:else}
                    <p class="text-sm text-gray-500">No interfaces defined</p>
                  {/if}
                </div>
                
                <h3 class="font-medium text-gray-900 mb-3 mt-4">Access Points</h3>
                <div class="flex flex-wrap gap-2 mb-4">
                  {#if viewingComponent.access_points && viewingComponent.access_points.length > 0 && viewingComponent.access_points[0]}
                    {#each viewingComponent.access_points.filter((a: string) => a) as accessPoint}
                      <span class="px-2 py-1 bg-white border border-gray-200 rounded text-sm">{accessPoint}</span>
                    {/each}
                  {:else}
                    <p class="text-sm text-gray-500">No access points defined</p>
                  {/if}
                </div>
                
                <h3 class="font-medium text-gray-900 mb-3 mt-4">Data Types</h3>
                <div class="flex flex-wrap gap-2 mb-4">
                  {#if viewingComponent.data_types && viewingComponent.data_types.length > 0 && viewingComponent.data_types[0]}
                    {#each viewingComponent.data_types.filter((d: string) => d) as dataType}
                      <span class="px-2 py-1 bg-white border border-gray-200 rounded text-sm">{dataType}</span>
                    {/each}
                  {:else}
                    <p class="text-sm text-gray-500">No data types defined</p>
                  {/if}
                </div>
                
                <h3 class="font-medium text-gray-900 mb-3 mt-4">Connected To</h3>
                <div class="flex flex-wrap gap-2">
                  {#if viewingComponent.connected_to && viewingComponent.connected_to.length > 0 && viewingComponent.connected_to[0]}
                    {#each viewingComponent.connected_to.filter((c: string) => c) as connectedId}
                      <span class="px-2 py-1 bg-white border border-gray-200 rounded text-sm">{connectedId}</span>
                    {/each}
                  {:else}
                    <p class="text-sm text-gray-500">Not connected to any components</p>
                  {/if}
                </div>
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t flex justify-end">
              <button 
                on:click={() => {
                  editingComponent = { ...viewingComponent };
                  viewingComponent = null;
                }}
                class="btn btn-primary flex items-center gap-2">
                <Edit size={16} />
                Edit Component
              </button>
            </div>
          </div>
        {:else}
          <!-- Regular Component Form for editing/creating -->
          <ComponentForm 
            editMode={!!editingComponent}
            component={editingComponent || undefined}
            availableComponents={components}
            on:submit={handleFormSubmit}
            on:cancel={handleFormCancel}
          />
        {/if}
      </div>
    </div>
  {/if}
  
  <!-- Import Modal -->
  <ComponentImport 
    isOpen={showImportModal}
    on:close={handleImportClose}
    on:import={handleImportSuccess}
  />
  
  <!-- Delete Confirmation Modal -->
  {#if showDeleteModal && componentToDelete}
    <div class="fixed inset-0 bg-neutral-900/40 z-50 flex items-center justify-center transition-opacity duration-200">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
        <div class="p-5 border-b border-gray-200">
          <div class="flex items-center">
            <div class="bg-red-100 p-2 rounded-full mr-3">
              <AlertTriangle size={24} class="text-red-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Delete Component</h3>
          </div>
        </div>
        
        <div class="p-5">
          <p class="text-gray-700 mb-2">Are you sure you want to delete this component?</p>
          <p class="font-medium text-gray-900 mb-1">{componentToDelete.name}</p>
          <p class="text-sm text-gray-500 mb-4">{componentToDelete.component_id}</p>
          
          <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <AlertTriangle size={20} class="text-red-600" />
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">
                  This action cannot be undone. This will permanently delete the component and remove all associated data.
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
