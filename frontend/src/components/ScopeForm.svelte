<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Edit, Save } from '@lucide/svelte';
  import { SystemType, type SystemScope } from '../api/scope';
  
  const dispatch = createEventDispatcher();
  
  // Form props
  export let editMode = false;
  export let viewMode = false; // New view-only mode
  export let scope: SystemScope | undefined = undefined;
  
  // Form state
  let formData = {
    name: '',
    scope_id: '',
    system_type: SystemType.SUBSYSTEM,
    description: '',
    boundaries: [] as string[],
    objectives: [] as string[],
    stakeholders: [] as string[]
  };
  
  // Temporary state for array inputs
  let newBoundary = '';
  let newObjective = '';
  let newStakeholder = '';
  
  // Initialize form data when mounted or when scope changes
  $: if (scope) {
    formData = {
      name: scope.name,
      scope_id: scope.scope_id,
      system_type: scope.system_type,
      description: scope.description || '',
      boundaries: [...(scope.boundaries || [])],
      objectives: [...(scope.objectives || [])],
      stakeholders: [...(scope.stakeholders || [])]
    };
  }
  
  // Ensure we've initialized the form with scope data
  onMount(() => {
    if (scope) {
      formData = {
        name: scope.name,
        scope_id: scope.scope_id,
        system_type: scope.system_type,
        description: scope.description || '',
        boundaries: [...(scope.boundaries || [])],
        objectives: [...(scope.objectives || [])],
        stakeholders: [...(scope.stakeholders || [])]
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
  
  function removeBoundary(index: number) {
    formData.boundaries = formData.boundaries.filter((_, i) => i !== index);
  }
  
  function removeObjective(index: number) {
    formData.objectives = formData.objectives.filter((_, i) => i !== index);
  }
  
  function removeStakeholder(index: number) {
    formData.stakeholders = formData.stakeholders.filter((_, i) => i !== index);
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="bg-white rounded-lg shadow-md overflow-hidden">
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold" style="color: var(--color-primary);">
        {#if viewMode}
          System Scope Details
        {:else if editMode}
          Edit System Scope
        {:else}
          Define New System Scope
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
          Scope Name <span class="text-red-500">*</span>
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
      
      <!-- System Type field -->
      <div>
        <label for="system-type" class="block text-sm font-medium text-gray-700 mb-1">
          System Type <span class="text-red-500">*</span>
        </label>
        {#if viewMode}
          <div class="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50">
            {formData.system_type}
          </div>
        {:else}
          <select 
            id="system-type" 
            bind:value={formData.system_type} 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value={SystemType.SUBSYSTEM}>Subsystem</option>
            <option value={SystemType.API}>API</option>
            <option value={SystemType.BACKEND}>Backend Service</option>
            <option value={SystemType.FULLSYSTEM}>Complete System</option>
            <option value={SystemType.EMBEDDED}>Embedded</option>
            <option value={SystemType.OTHER}>Other</option>
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
        {editMode ? 'Update Scope' : 'Create Scope'}
      </button>
    {/if}
  </div>
</form>
