<script lang="ts">
  import { onMount } from 'svelte';
  import { getThreatCatalogItems, deleteThreatCatalogItem, type ThreatCatalogItem, StrideCategory } from '../../api/threat';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  import Modal from '../ui/Modal.svelte';
  import ThreatCatalogForm from './ThreatCatalogForm.svelte';
  import ThreatCatalogDetails from './ThreatCatalogDetails.svelte';
  import { fade } from 'svelte/transition';
  
  // State variables
  let catalogItems: ThreatCatalogItem[] = [];
  let loading = true;
  let error = '';
  let selectedThreatId: string | null = null;
  let threatToDelete: ThreatCatalogItem | null = null;
  let showDeleteConfirmation = false;
  let showCreateForm = false;
  let showEditForm = false;
  let showDetails = false;
  let filterByCategory: string = '';
  
  // STRIDE category display names
  const strideCategoryNames = {
    [StrideCategory.SPOOFING]: 'Spoofing',
    [StrideCategory.TAMPERING]: 'Tampering',
    [StrideCategory.REPUDIATION]: 'Repudiation',
    [StrideCategory.INFO_DISCLOSURE]: 'Information Disclosure',
    [StrideCategory.DENIAL_OF_SERVICE]: 'Denial of Service',
    [StrideCategory.ELEVATION]: 'Elevation of Privilege'
  };
  
  // Functions
  function handleCreateClick() {
    showCreateForm = true;
  }
  
  function handleEditClick(item: ThreatCatalogItem) {
    selectedThreatId = item.id;
    showEditForm = true;
  }
  
  function handleViewClick(item: ThreatCatalogItem) {
    selectedThreatId = item.id;
    showDetails = true;
  }
  
  function handleDeleteClick(item: ThreatCatalogItem) {
    threatToDelete = item;
    showDeleteConfirmation = true;
  }
  
  function closeModals() {
    showCreateForm = false;
    showEditForm = false;
    showDetails = false;
    showDeleteConfirmation = false;
    selectedThreatId = null;
    threatToDelete = null;
  }
  
  async function confirmDelete() {
    if (threatToDelete) {
      try {
        await deleteThreatCatalogItem(threatToDelete.id);
        showNotification('Threat catalog item deleted successfully', 'success');
        catalogItems = catalogItems.filter(item => item.id !== threatToDelete?.id);
        closeModals();
      } catch (err) {
        console.error('Error deleting threat catalog item:', err);
        showNotification('Failed to delete threat catalog item', 'error');
      }
    }
  }
  
  async function loadCatalogItems() {
    loading = true;
    error = '';
    
    try {
      const result = await getThreatCatalogItems(0, 100);
      catalogItems = result.catalog_items;
    } catch (err) {
      console.error('Error loading threat catalog:', err);
      error = 'Failed to load threat catalog';
      showNotification('Failed to load threat catalog', 'error');
    } finally {
      loading = false;
    }
  }
  
  function handleThreatCreated(event: CustomEvent<ThreatCatalogItem>) {
    const newThreat = event.detail;
    catalogItems = [...catalogItems, newThreat];
    closeModals();
    showNotification('Threat catalog item created successfully', 'success');
  }
  
  function handleThreatUpdated(event: CustomEvent<ThreatCatalogItem>) {
    const updatedThreat = event.detail;
    catalogItems = catalogItems.map(item => 
      item.id === updatedThreat.id ? updatedThreat : item
    );
    closeModals();
    showNotification('Threat catalog item updated successfully', 'success');
  }
  
  // Filter functions
  $: filteredCatalogItems = filterByCategory 
    ? catalogItems.filter(item => item.stride_category === filterByCategory) 
    : catalogItems;
  
  // Load items on mount
  onMount(() => {
    loadCatalogItems();
  });
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-semibold mb-6">STRIDE Threat Catalog</h1>
  
  <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
    <div class="w-full sm:w-auto">
      <label for="categoryFilter" class="block mb-1 text-sm font-medium">Filter by STRIDE Category:</label>
      <select 
        id="categoryFilter" 
        bind:value={filterByCategory} 
        class="p-2 border rounded-md w-full sm:w-auto"
      >
        <option value="">All Categories</option>
        {#each Object.entries(StrideCategory) as [key, value]}
          <option value={value}>{strideCategoryNames[value]}</option>
        {/each}
      </select>
    </div>
    
    <button 
      on:click={handleCreateClick}
      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 3a1 1 0 00-1 1v5H4a1 1 0 100 2h5v5a1 1 0 102 0v-5h5a1 1 0 100-2h-5V4a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      Add New Threat
    </button>
  </div>
  
  {#if loading}
    <div class="flex justify-center py-12">
      <Spinner size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {error}</span>
    </div>
  {:else if filteredCatalogItems.length === 0}
    <div class="bg-gray-100 text-gray-700 px-4 py-12 rounded-md text-center">
      {filterByCategory ? 'No threats found in this category.' : 'No threats found in the catalog.'}
      <div class="mt-4">
        <button 
          on:click={handleCreateClick}
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md inline-flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 00-1 1v5H4a1 1 0 100 2h5v5a1 1 0 102 0v-5h5a1 1 0 100-2h-5V4a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          Create First Threat
        </button>
      </div>
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Likelihood</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          {#each filteredCatalogItems as item (item.id)}
            <tr transition:fade={{ duration: 200 }} class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 cursor-pointer hover:text-blue-600" 
                     on:click={() => handleViewClick(item)}>
                  {item.title}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                  {item.stride_category === StrideCategory.SPOOFING ? 'bg-purple-100 text-purple-800' : 
                   item.stride_category === StrideCategory.TAMPERING ? 'bg-yellow-100 text-yellow-800' : 
                   item.stride_category === StrideCategory.REPUDIATION ? 'bg-blue-100 text-blue-800' : 
                   item.stride_category === StrideCategory.INFO_DISCLOSURE ? 'bg-green-100 text-green-800' : 
                   item.stride_category === StrideCategory.DENIAL_OF_SERVICE ? 'bg-red-100 text-red-800' : 
                   'bg-orange-100 text-orange-800'}">
                  {strideCategoryNames[item.stride_category]}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="relative w-20 h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div class="absolute top-0 left-0 h-full rounded-full 
                      {item.typical_likelihood <= 2 ? 'bg-green-500' : 
                      item.typical_likelihood <= 4 ? 'bg-yellow-500' : 'bg-red-500'}"
                      style="width: {item.typical_likelihood * 20}%"></div>
                  </div>
                  <span class="ml-2 text-sm text-gray-700">{item.typical_likelihood}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="relative w-20 h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div class="absolute top-0 left-0 h-full rounded-full 
                      {item.typical_severity <= 2 ? 'bg-green-500' : 
                      item.typical_severity <= 4 ? 'bg-yellow-500' : 'bg-red-500'}"
                      style="width: {item.typical_severity * 20}%"></div>
                  </div>
                  <span class="ml-2 text-sm text-gray-700">{item.typical_severity}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex space-x-2">
                  <button 
                    on:click={() => handleViewClick(item)} 
                    class="text-blue-600 hover:text-blue-900"
                    title="View details"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <button 
                    on:click={() => handleEditClick(item)} 
                    class="text-yellow-600 hover:text-yellow-900"
                    title="Edit"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button 
                    on:click={() => handleDeleteClick(item)} 
                    class="text-red-600 hover:text-red-900"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
  
  <!-- Create Threat Modal -->
  {#if showCreateForm}
    <Modal on:close={closeModals} title="Create New Threat">
      <ThreatCatalogForm on:created={handleThreatCreated} on:cancel={closeModals} />
    </Modal>
  {/if}
  
  <!-- Edit Threat Modal -->
  {#if showEditForm && selectedThreatId}
    <Modal on:close={closeModals} title="Edit Threat">
      <ThreatCatalogForm 
        threatId={selectedThreatId} 
        mode="edit" 
        on:updated={handleThreatUpdated} 
        on:cancel={closeModals} 
      />
    </Modal>
  {/if}
  
  <!-- View Threat Details Modal -->
  {#if showDetails && selectedThreatId}
    <Modal on:close={closeModals} title="Threat Details">
      <ThreatCatalogDetails 
        threatId={selectedThreatId} 
        on:edit={() => {
          showDetails = false;
          showEditForm = true;
        }} 
        on:close={closeModals} 
      />
    </Modal>
  {/if}
  
  <!-- Delete Confirmation Modal -->
  {#if showDeleteConfirmation && threatToDelete}
    <Modal on:close={closeModals} title="Confirm Deletion">
      <div class="p-6">
        <p class="mb-4">Are you sure you want to delete the threat "{threatToDelete.title}"?</p>
        <p class="mb-6 text-red-600 text-sm">This action cannot be undone.</p>
        
        <div class="flex justify-end space-x-3">
          <button 
            on:click={closeModals}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md"
          >
            Cancel
          </button>
          <button 
            on:click={confirmDelete}
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
          >
            Delete
          </button>
        </div>
      </div>
    </Modal>
  {/if}
</div>
