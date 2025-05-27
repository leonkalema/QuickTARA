<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Edit, Save } from '@lucide/svelte';
  import { AssetType, SecurityLevel, type Asset } from '../api/assets';
  import { productApi, type Product } from '../api/products';
  import { safeApiCall } from '../utils/error-handler';
  
  const dispatch = createEventDispatcher();
  
  // Form props
  export let editMode = false;
  export let viewMode = false;
  export let asset: Asset | undefined = undefined;
  export let preselectedProductId: string | null = null; // Optional pre-selected product
  
  // Form state
  let formData = {
    asset_id: '',
    name: '',
    description: '',
    asset_type: AssetType.SOFTWARE,
    data_types: [] as string[],
    storage_location: '',
    scope_id: '',
    confidentiality: SecurityLevel.MEDIUM,
    integrity: SecurityLevel.MEDIUM,
    availability: SecurityLevel.MEDIUM,
    authenticity_required: false,
    authorization_required: false
  };
  
  // Available products for selection
  let products: Product[] = [];
  
  // Temporary state for array inputs
  let newDataType = '';
  
  // Initialize form data when asset changes
  $: if (asset) {
    formData = {
      asset_id: asset.asset_id,
      name: asset.name,
      description: asset.description || '',
      asset_type: asset.asset_type,
      data_types: [...(asset.data_types || [])],
      storage_location: asset.storage_location || '',
      scope_id: asset.scope_id,
      confidentiality: asset.confidentiality,
      integrity: asset.integrity,
      availability: asset.availability,
      authenticity_required: asset.authenticity_required,
      authorization_required: asset.authorization_required
    };
  }
  
  // Load products on mount
  onMount(async () => {
    try {
      // Initialize the form with asset data if provided
      if (asset) {
        formData = {
          asset_id: asset.asset_id,
          name: asset.name,
          description: asset.description || '',
          asset_type: asset.asset_type,
          data_types: [...(asset.data_types || [])],
          storage_location: asset.storage_location || '',
          scope_id: asset.scope_id,
          confidentiality: asset.confidentiality,
          integrity: asset.integrity,
          availability: asset.availability,
          authenticity_required: asset.authenticity_required,
          authorization_required: asset.authorization_required
        };
      }
      
      // Set pre-selected product if provided
      if (preselectedProductId && !formData.scope_id) {
        formData.scope_id = preselectedProductId;
      }
      
      // Load available products for scope selection
      const result = await safeApiCall(() => productApi.getAll());
      if (result) {
        products = result.scopes;
      }
    } catch (err) {
      console.error('Error initializing asset form:', err);
    }
  });
  
  function handleSubmit() {
    // Create a copy of form data to send
    const formPayload = { ...formData };
    
    // Remove asset_id if not in edit mode (API will generate one)
    if (!editMode) {
      const { asset_id, ...rest } = formPayload;
      return dispatch('submit', rest);
    }
    
    dispatch('submit', formPayload);
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
  
  function handleEdit() {
    // Switch from view mode to edit mode
    viewMode = false;
    editMode = true;
    // Dispatch an event so parent knows we switched to edit mode
    dispatch('switchToEdit');
  }
  
  // Handle array inputs
  function addDataType() {
    if (newDataType.trim()) {
      formData.data_types = [...formData.data_types, newDataType.trim()];
      newDataType = '';
    }
  }
  
  function removeDataType(index: number) {
    formData.data_types = formData.data_types.filter((_, i) => i !== index);
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="bg-white rounded-lg shadow-md overflow-hidden">
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold" style="color: var(--color-primary);">
        {#if viewMode}
          Asset Details
        {:else if editMode}
          Edit Asset
        {:else}
          New Asset
        {/if}
      </h2>
      <div class="flex items-center gap-2">
        {#if viewMode}
          <button 
            type="button" 
            on:click={handleEdit}
            class="text-blue-600 hover:text-blue-800 p-1 rounded-full hover:bg-blue-100">
            <Edit size={20} />
          </button>
        {/if}
        <button 
          type="button" 
          on:click={handleCancel}
          class="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100">
          <X size={24} />
        </button>
      </div>
    </div>
    
    <div class="space-y-6">
      <!-- Product Selection field -->
      <div>
        <label for="product-select" class="block text-sm font-medium text-gray-700 mb-1">
          Product <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {products.find(p => p.scope_id === formData.scope_id)?.name || formData.scope_id}
          </div>
        {:else}
          <select
            id="product-select"
            bind:value={formData.scope_id}
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="" disabled selected>Select a product...</option>
            {#each products as product}
              <option value={product.scope_id}>{product.name} ({product.product_type})</option>
            {/each}
          </select>
        {/if}
      </div>
      
      <!-- Name field -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
          Asset Name <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.name}
          </div>
        {:else}
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
            placeholder="e.g., ECU Firmware"
          />
        {/if}
      </div>
      
      <!-- Asset Type field -->
      <div>
        <label for="asset-type" class="block text-sm font-medium text-gray-700 mb-1">
          Asset Type <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.asset_type}
          </div>
        {:else}
          <select
            id="asset-type"
            bind:value={formData.asset_type}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value={AssetType.FIRMWARE}>Firmware</option>
            <option value={AssetType.SOFTWARE}>Software</option>
            <option value={AssetType.CONFIGURATION}>Configuration</option>
            <option value={AssetType.CALIBRATION}>Calibration</option>
            <option value={AssetType.DATA}>Data</option>
            <option value={AssetType.DIAGNOSTIC}>Diagnostic</option>
            <option value={AssetType.COMMUNICATION}>Communication</option>
            <option value={AssetType.HARDWARE}>Hardware</option>
            <option value={AssetType.INTERFACE}>Interface</option>
            <option value={AssetType.OTHER}>Other</option>
          </select>
        {/if}
      </div>
      
      <!-- Description field -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 min-h-24">
            {formData.description || 'No description provided.'}
          </div>
        {:else}
          <textarea
            id="description"
            bind:value={formData.description}
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
            placeholder="Describe the asset's purpose and function"
          ></textarea>
        {/if}
      </div>
      
      <!-- Storage Location field -->
      <div>
        <label for="storage-location" class="block text-sm font-medium text-gray-700 mb-1">
          Storage Location
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.storage_location || 'Not specified'}
          </div>
        {:else}
          <input
            type="text"
            id="storage-location"
            bind:value={formData.storage_location}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
            placeholder="e.g., Internal Flash Memory, External Database"
          />
        {/if}
      </div>
      
      <!-- Data Types field -->
      <div>
        <label for="data-type" class="block text-sm font-medium text-gray-700 mb-1">
          Data Types
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="data-type"
              bind:value={newDataType} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., Configuration Data, User Credentials, Sensor Values"
            />
            <button 
              type="button"
              on:click={addDataType}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.data_types.length > 0}
              {#each formData.data_types as dataType}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{dataType}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No data types defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.data_types.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.data_types as dataType, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{dataType}</span>
                <button 
                  type="button"
                  on:click={() => removeDataType(i)}
                  class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-100"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Remove">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  <span class="sr-only">Remove</span>
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </div>
      
      <!-- Security Properties Section -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <h3 class="text-lg font-medium text-gray-900">Security Properties</h3>
          <div class="group relative">
            <button 
              type="button" 
              class="text-blue-500 hover:text-blue-700 focus:outline-none"
              aria-label="More information about security properties"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 16v-4"></path>
                <path d="M12 8h.01"></path>
              </svg>
            </button>
            <div class="invisible group-hover:visible absolute z-10 w-72 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 bottom-full mb-2">
              <p class="mb-1">Security properties help identify protection requirements for this asset according to ISO/SAE 21434.</p>
              <p>Higher ratings indicate greater security needs and will influence threat analysis and risk assessment.</p>
            </div>
          </div>
        </div>
        <div class="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-md text-sm text-blue-800">
          Rate each property based on the potential impact if that security aspect was compromised. Higher ratings indicate greater protection is needed.
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <!-- Confidentiality -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label for="confidentiality" class="block text-sm font-medium text-gray-700">
                Confidentiality
              </label>
              <div class="group relative inline-block">
                <button 
                  type="button" 
                  class="text-xs text-blue-500 hover:text-blue-700 focus:outline-none" 
                  aria-label="More information about confidentiality"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M12 8h.01"></path>
                  </svg>
                </button>
                <div class="invisible group-hover:visible absolute z-10 w-64 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 top-full mt-1">
                  <p class="font-semibold mb-1">Confidentiality:</p>
                  <p class="mb-1"><b>High</b>: Unauthorized disclosure would cause significant damage (e.g., proprietary algorithms, cryptographic keys)</p>
                  <p class="mb-1"><b>Medium</b>: Disclosure would cause limited damage</p>
                  <p><b>Low</b>: Minimal impact if disclosed</p>
                </div>
              </div>
            </div>
            {#if viewMode}
              <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
                {formData.confidentiality}
              </div>
            {:else}
              <select
                id="confidentiality"
                bind:value={formData.confidentiality}
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value={SecurityLevel.HIGH}>High</option>
                <option value={SecurityLevel.MEDIUM}>Medium</option>
                <option value={SecurityLevel.LOW}>Low</option>
                <option value={SecurityLevel.NOT_APPLICABLE}>N/A</option>
              </select>
            {/if}
          </div>
          
          <!-- Integrity -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label for="integrity" class="block text-sm font-medium text-gray-700">
                Integrity
              </label>
              <div class="group relative inline-block">
                <button 
                  type="button" 
                  class="text-xs text-blue-500 hover:text-blue-700 focus:outline-none" 
                  aria-label="More information about integrity"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M12 8h.01"></path>
                  </svg>
                </button>
                <div class="invisible group-hover:visible absolute z-10 w-64 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 top-full mt-1">
                  <p class="font-semibold mb-1">Integrity:</p>
                  <p class="mb-1"><b>High</b>: Alteration could lead to critical safety impacts (e.g., safety-critical software, firmware)</p>
                  <p class="mb-1"><b>Medium</b>: Alteration could affect functionality but not safety</p>
                  <p><b>Low</b>: Minimal impact if altered</p>
                </div>
              </div>
            </div>
            {#if viewMode}
              <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
                {formData.integrity}
              </div>
            {:else}
              <select
                id="integrity"
                bind:value={formData.integrity}
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value={SecurityLevel.HIGH}>High</option>
                <option value={SecurityLevel.MEDIUM}>Medium</option>
                <option value={SecurityLevel.LOW}>Low</option>
                <option value={SecurityLevel.NOT_APPLICABLE}>N/A</option>
              </select>
            {/if}
          </div>
          
          <!-- Availability -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label for="availability" class="block text-sm font-medium text-gray-700">
                Availability
              </label>
              <div class="group relative inline-block">
                <button 
                  type="button" 
                  class="text-xs text-blue-500 hover:text-blue-700 focus:outline-none" 
                  aria-label="More information about availability"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M12 8h.01"></path>
                  </svg>
                </button>
                <div class="invisible group-hover:visible absolute z-10 w-64 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 top-full mt-1">
                  <p class="font-semibold mb-1">Availability:</p>
                  <p class="mb-1"><b>High</b>: System cannot function if this asset is unavailable (e.g., core ECU firmware)</p>
                  <p class="mb-1"><b>Medium</b>: Limited functionality possible without this asset</p>
                  <p><b>Low</b>: System can function without this asset</p>
                </div>
              </div>
            </div>
            {#if viewMode}
              <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
                {formData.availability}
              </div>
            {:else}
              <select
                id="availability"
                bind:value={formData.availability}
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value={SecurityLevel.HIGH}>High</option>
                <option value={SecurityLevel.MEDIUM}>Medium</option>
                <option value={SecurityLevel.LOW}>Low</option>
                <option value={SecurityLevel.NOT_APPLICABLE}>N/A</option>
              </select>
            {/if}
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Authentication Required -->
          <div>
            {#if viewMode}
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-700">Authenticity Required:</span>
                <span class="ml-2 text-sm text-gray-900">{formData.authenticity_required ? 'Yes' : 'No'}</span>
              </div>
            {:else}
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="authenticity-required"
                      bind:checked={formData.authenticity_required}
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span class="ml-2 text-sm font-medium text-gray-700">Authenticity Required</span>
                  </label>
                  <div class="group relative inline-block">
                    <button 
                      type="button" 
                      class="text-xs text-blue-500 hover:text-blue-700 focus:outline-none" 
                      aria-label="More information about authenticity requirement"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 16v-4"></path>
                        <path d="M12 8h.01"></path>
                      </svg>
                    </button>
                    <div class="invisible group-hover:visible absolute z-10 w-64 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 top-full mt-1">
                      <p class="font-semibold mb-1">Authenticity Required:</p>
                      <p>Enable when the system must verify this asset is genuine before using it. Applies to assets like firmware, software updates, or security-related configuration that need verification for their legitimacy.</p>
                    </div>
                  </div>
                </div>
                <p class="text-xs text-gray-500 ml-6">Ensures the asset is genuine and from a trusted source</p>
              </div>
            {/if}
          </div>
          
          <!-- Authorization Required -->
          <div>
            {#if viewMode}
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-700">Authorization Required:</span>
                <span class="ml-2 text-sm text-gray-900">{formData.authorization_required ? 'Yes' : 'No'}</span>
              </div>
            {:else}
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="authorization-required"
                      bind:checked={formData.authorization_required}
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span class="ml-2 text-sm font-medium text-gray-700">Authorization Required</span>
                  </label>
                  <div class="group relative inline-block">
                    <button 
                      type="button" 
                      class="text-xs text-blue-500 hover:text-blue-700 focus:outline-none" 
                      aria-label="More information about authorization requirement"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 16v-4"></path>
                        <path d="M12 8h.01"></path>
                      </svg>
                    </button>
                    <div class="invisible group-hover:visible absolute z-10 w-64 bg-gray-800 text-white text-xs rounded py-2 px-3 right-0 top-full mt-1">
                      <p class="font-semibold mb-1">Authorization Required:</p>
                      <p>Enable when specific permissions are needed to access or modify this asset. Relevant for sensitive assets that should only be accessed by certain roles or users with appropriate privileges.</p>
                    </div>
                  </div>
                </div>
                <p class="text-xs text-gray-500 ml-6">Controls who can access or modify this asset</p>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3 border-t">
    <button
      type="button"
      on:click={handleCancel}
      class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
    >
      {viewMode ? 'Close' : 'Cancel'}
    </button>
    
    {#if !viewMode}
      <button
        type="submit"
        class="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center gap-2"
      >
        <Save size={16} />
        {editMode ? 'Update Asset' : 'Create Asset'}
      </button>
    {/if}
  </div>
</form>
