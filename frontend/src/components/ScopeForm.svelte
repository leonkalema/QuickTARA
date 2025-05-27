<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Edit, Save } from '@lucide/svelte';
  import { ProductType, SafetyLevel, TrustZone, type Product } from '../api/products';
  
  const dispatch = createEventDispatcher();
  
  // Form props
  export let editMode = false;
  export let viewMode = false; // New view-only mode
  export let scope: Product | undefined = undefined;
  
  // Form state
  let formData = {
    name: '',
    scope_id: '',
    product_type: ProductType.ECU,
    description: '',
    boundaries: [] as string[],
    objectives: [] as string[],
    stakeholders: [] as string[],
    // New product-specific fields
    safety_level: SafetyLevel.ASIL_D,
    interfaces: [] as string[],
    access_points: [] as string[],
    location: 'Internal',
    trust_zone: TrustZone.CRITICAL
  };
  
  // Temporary state for array inputs
  let newBoundary = '';
  let newObjective = '';
  let newStakeholder = '';
  let newInterface = '';
  let newAccessPoint = '';
  
  // Initialize form data when mounted or when scope changes
  $: if (scope) {
    formData = {
      name: scope.name,
      scope_id: scope.scope_id,
      product_type: scope.product_type,
      description: scope.description || '',
      boundaries: [...(scope.boundaries || [])],
      objectives: [...(scope.objectives || [])],
      stakeholders: [...(scope.stakeholders || [])],
      // New product-specific fields
      safety_level: scope.safety_level,
      interfaces: [...(scope.interfaces || [])],
      access_points: [...(scope.access_points || [])],
      location: scope.location,
      trust_zone: scope.trust_zone
    };
  }
  
  // Ensure we've initialized the form with scope data
  onMount(() => {
    if (scope) {
      formData = {
        name: scope.name,
        scope_id: scope.scope_id,
        product_type: scope.product_type,
        description: scope.description || '',
        boundaries: [...(scope.boundaries || [])],
        objectives: [...(scope.objectives || [])],
        stakeholders: [...(scope.stakeholders || [])],
        // New product-specific fields
        safety_level: scope.safety_level,
        interfaces: [...(scope.interfaces || [])],
        access_points: [...(scope.access_points || [])],
        location: scope.location,
        trust_zone: scope.trust_zone
      };
    }
  });
  
  function handleSubmit() {
    // Create a copy of form data to send
    const formPayload = { ...formData };
    
    // Remove scope_id if not in edit mode (API will generate one)
    if (!editMode) {
      const { scope_id, ...rest } = formPayload;
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
  function addBoundary() {
    if (newBoundary.trim()) {
      formData.boundaries = [...formData.boundaries, newBoundary.trim()];
      newBoundary = '';
    }
  }
  
  function addObjective() {
    if (newObjective.trim()) {
      formData.objectives = [...formData.objectives, newObjective.trim()];
      newObjective = '';
    }
  }
  
  function addStakeholder() {
    if (newStakeholder.trim()) {
      formData.stakeholders = [...formData.stakeholders, newStakeholder.trim()];
      newStakeholder = '';
    }
  }
  
  function addInterface() {
    if (newInterface.trim()) {
      formData.interfaces = [...formData.interfaces, newInterface.trim()];
      newInterface = '';
    }
  }
  
  function addAccessPoint() {
    if (newAccessPoint.trim()) {
      formData.access_points = [...formData.access_points, newAccessPoint.trim()];
      newAccessPoint = '';
    }
  }
  
  function removeBoundary(index: number) {
    formData.boundaries = formData.boundaries.filter((_, i) => i !== index);
  }
  
  function removeObjective(index: number) {
    formData.objectives = formData.objectives.filter((_, i) => i !== index);
  }
  
  function removeStakeholder(index: number) {
    formData.stakeholders = formData.stakeholders.filter((_, i) => i !== index);
  }
  
  function removeInterface(index: number) {
    formData.interfaces = formData.interfaces.filter((_, i) => i !== index);
  }
  
  function removeAccessPoint(index: number) {
    formData.access_points = formData.access_points.filter((_, i) => i !== index);
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="bg-white rounded-lg shadow-md overflow-hidden">
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold" style="color: var(--color-primary);">
        {#if viewMode}
          Product Details
        {:else if editMode}
          Edit Product
        {:else}
          Define New Product
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
      <!-- Name field -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
          Product Name <span class="text-red-500">*</span>
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
            placeholder="e.g., In-Vehicle Infotainment System"
          />
        {/if}
      </div>
      
      <!-- Product Type field -->
      <div>
        <label for="product-type" class="block text-sm font-medium text-gray-700 mb-1">
          Product Type <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.product_type}
          </div>
        {:else}
          <select
            id="product-type"
            bind:value={formData.product_type}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value={ProductType.ECU}>ECU</option>
            <option value={ProductType.GATEWAY}>Gateway</option>
            <option value={ProductType.SENSOR}>Sensor</option>
            <option value={ProductType.ACTUATOR}>Actuator</option>
            <option value={ProductType.NETWORK}>Network</option>
            <option value={ProductType.EXTERNAL_DEVICE}>External Device</option>
            <option value={ProductType.OTHER}>Other</option>
          </select>
        {/if}
      </div>
      
      <!-- Safety Level field -->
      <div>
        <label for="safety-level" class="block text-sm font-medium text-gray-700 mb-1">
          Safety Level <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.safety_level}
          </div>
        {:else}
          <select
            id="safety-level"
            bind:value={formData.safety_level}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value={SafetyLevel.QM}>QM</option>
            <option value={SafetyLevel.ASIL_A}>ASIL A</option>
            <option value={SafetyLevel.ASIL_B}>ASIL B</option>
            <option value={SafetyLevel.ASIL_C}>ASIL C</option>
            <option value={SafetyLevel.ASIL_D}>ASIL D</option>
          </select>
        {/if}
      </div>
      
      <!-- Location field -->
      <div>
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">
          Location <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.location}
          </div>
        {:else}
          <select
            id="location"
            bind:value={formData.location}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="Internal">Internal</option>
            <option value="External">External</option>
            <option value="Boundary">Boundary</option>
          </select>
        {/if}
      </div>
      
      <!-- Trust Zone field -->
      <div>
        <label for="trust-zone" class="block text-sm font-medium text-gray-700 mb-1">
          Trust Zone <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.trust_zone}
          </div>
        {:else}
          <select
            id="trust-zone"
            bind:value={formData.trust_zone}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value={TrustZone.CRITICAL}>Critical</option>
            <option value={TrustZone.BOUNDARY}>Boundary</option>
            <option value={TrustZone.STANDARD}>Standard</option>
            <option value={TrustZone.UNTRUSTED}>Untrusted</option>
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
            {formData.description || 'No description provided'}
          </div>
        {:else}
          <textarea 
            id="description" 
            bind:value={formData.description} 
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
            placeholder="Describe the system or subsystem and its primary functions"
          ></textarea>
        {/if}
      </div>
      
      <!-- Interfaces field -->
      <div>
        <label for="interface" class="block text-sm font-medium text-gray-700 mb-1">
          Interfaces
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="interface"
              bind:value={newInterface} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., CAN, Ethernet, USB"
            />
            <button 
              type="button"
              on:click={addInterface}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.interfaces.length > 0}
              {#each formData.interfaces as interfaceItem}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{interfaceItem}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No interfaces defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.interfaces.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.interfaces as interfaceItem, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{interfaceItem}</span>
                <button 
                  type="button"
                  on:click={() => removeInterface(i)}
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
      
      <!-- Access Points field -->
      <div>
        <label for="access-point" class="block text-sm font-medium text-gray-700 mb-1">
          Access Points
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="access-point"
              bind:value={newAccessPoint} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., OBD-II, Debug Port"
            />
            <button 
              type="button"
              on:click={addAccessPoint}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.access_points.length > 0}
              {#each formData.access_points as access_point}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{access_point}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No access points defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.access_points.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.access_points as access_point, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{access_point}</span>
                <button 
                  type="button"
                  on:click={() => removeAccessPoint(i)}
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
      
      <!-- Boundaries field -->
      <div>
        <label for="system-boundary" class="block text-sm font-medium text-gray-700 mb-1">
          System Boundaries
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="system-boundary"
              bind:value={newBoundary} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., Vehicle Connectivity Interface"
            />
            <button 
              type="button"
              on:click={addBoundary}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.boundaries.length > 0}
              {#each formData.boundaries as boundary}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{boundary}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No boundaries defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.boundaries.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.boundaries as boundary, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{boundary}</span>
                <button 
                  type="button"
                  on:click={() => removeBoundary(i)}
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
      
      <!-- Objectives field -->
      <div>
        <label for="system-objective" class="block text-sm font-medium text-gray-700 mb-1">
          System Objectives
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="system-objective"
              bind:value={newObjective} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., Provide navigation services to driver"
            />
            <button 
              type="button"
              on:click={addObjective}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.objectives.length > 0}
              {#each formData.objectives as objective}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{objective}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No objectives defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.objectives.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.objectives as objective, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{objective}</span>
                <button 
                  type="button"
                  on:click={() => removeObjective(i)}
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
      
      <!-- Stakeholders field -->
      <div>
        <label for="stakeholder" class="block text-sm font-medium text-gray-700 mb-1">
          Stakeholders
        </label>
        {#if !viewMode}
          <div class="flex mb-2">
            <input 
              type="text" 
              id="stakeholder"
              bind:value={newStakeholder} 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., Vehicle Owners, Maintenance Personnel"
            />
            <button 
              type="button"
              on:click={addStakeholder}
              class="px-4 py-2 bg-gray-100 border border-gray-300 border-l-0 rounded-r-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
        {/if}
        {#if viewMode}
          <div class="mt-2 space-y-2">
            {#if formData.stakeholders.length > 0}
              {#each formData.stakeholders as stakeholder}
                <div class="bg-gray-50 p-2 rounded-md">
                  <span class="text-sm">{stakeholder}</span>
                </div>
              {/each}
            {:else}
              <div class="bg-gray-50 p-2 rounded-md text-gray-500 italic">
                <span class="text-sm">No stakeholders defined</span>
              </div>
            {/if}
          </div>
        {:else if formData.stakeholders.length > 0}
          <div class="mt-2 space-y-2">
            {#each formData.stakeholders as stakeholder, i}
              <div class="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span class="text-sm">{stakeholder}</span>
                <button 
                  type="button"
                  on:click={() => removeStakeholder(i)}
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
        {editMode ? 'Update Product' : 'Create Product'}
      </button>
    {/if}
  </div>
</form>
