<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { X, Save, Plus, Trash2 } from '@lucide/svelte';
  
  // Default component types and safety levels
  const componentTypes = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network'];
  const safetyLevels = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D'];
  const trustZones = ['Critical', 'Boundary', 'Standard', 'Untrusted'];
  const locations = ['Internal', 'External'];
  
  // Component input
  export let editMode = false;
  export let component = {
    component_id: '',
    name: '',
    type: componentTypes[0],
    safety_level: safetyLevels[0],
    interfaces: [''],
    access_points: [''],
    data_types: [''],
    location: locations[0],
    trust_zone: trustZones[0],
    connected_to: ['']
  };
  
  // Available components for connection selection
  export let availableComponents: { component_id: string; name: string; }[] = [];
  
  const dispatch = createEventDispatcher();
  
  function handleSubmit() {
    // Filter out empty values from arrays
    const cleanedComponent = {
      ...component,
      interfaces: component.interfaces.filter(i => i.trim() !== ''),
      access_points: component.access_points.filter(a => a.trim() !== ''),
      data_types: component.data_types.filter(d => d.trim() !== ''),
      connected_to: component.connected_to.filter(c => c.trim() !== '')
    };
    
    dispatch('submit', cleanedComponent);
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
  
  // Helper functions for dynamic arrays
  function addItem(array: string[], initial = '') {
    return [...array, initial];
  }
  
  function removeItem(array: string[], index: number) {
    return array.filter((_, i) => i !== index);
  }
  
  function updateItem(array: string[], index: number, value: string) {
    return array.map((item, i) => i === index ? value : item);
  }
</script>

<div class="bg-white rounded-xl shadow-md p-6 max-w-2xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-bold text-gray-900">
      {editMode ? 'Edit Component' : 'Add New Component'}
    </h2>
    <button 
      on:click={handleCancel}
      class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
      <X size={20} />
    </button>
  </div>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
      <!-- Component ID -->
      <div>
        <label for="component_id" class="block text-sm font-medium text-gray-700 mb-1">Component ID *</label>
        <input 
          type="text" 
          id="component_id" 
          bind:value={component.component_id}
          required
          disabled={editMode}
          class="w-full rounded-md {editMode ? 'bg-gray-100' : ''}"
          placeholder="ECU001"
        />
      </div>
      
      <!-- Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
        <input 
          type="text" 
          id="name" 
          bind:value={component.name}
          required
          class="w-full rounded-md"
          placeholder="Engine Control Unit"
        />
      </div>
      
      <!-- Type -->
      <div>
        <label for="type" class="block text-sm font-medium text-gray-700 mb-1">Type *</label>
        <select 
          id="type" 
          bind:value={component.type}
          required
          class="w-full rounded-md">
          {#each componentTypes as type}
            <option value={type}>{type}</option>
          {/each}
        </select>
      </div>
      
      <!-- Safety Level -->
      <div>
        <label for="safety_level" class="block text-sm font-medium text-gray-700 mb-1">Safety Level *</label>
        <select 
          id="safety_level" 
          bind:value={component.safety_level}
          required
          class="w-full rounded-md">
          {#each safetyLevels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </div>
      
      <!-- Location -->
      <div>
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location *</label>
        <select 
          id="location" 
          bind:value={component.location}
          required
          class="w-full rounded-md">
          {#each locations as location}
            <option value={location}>{location}</option>
          {/each}
        </select>
      </div>
      
      <!-- Trust Zone -->
      <div>
        <label for="trust_zone" class="block text-sm font-medium text-gray-700 mb-1">Trust Zone *</label>
        <select 
          id="trust_zone" 
          bind:value={component.trust_zone}
          required
          class="w-full rounded-md">
          {#each trustZones as zone}
            <option value={zone}>{zone}</option>
          {/each}
        </select>
      </div>
    </div>
    
    <!-- Interfaces (Array) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Interfaces</label>
      <div class="space-y-2">
        {#each component.interfaces as interfaceItem, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              bind:value={component.interfaces[index]}
              on:input={() => component.interfaces = updateItem(component.interfaces, index, component.interfaces[index])}
              class="flex-1 rounded-md"
              placeholder="CAN, FlexRay, etc."
            />
            {#if index === component.interfaces.length - 1}
              <button 
                type="button"
                on:click={() => component.interfaces = addItem(component.interfaces)}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.interfaces = removeItem(component.interfaces, index)}
                class="p-2 bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 rounded-md transition-colors"
              >
                <Trash2 size={16} />
              </button>
            {/if}
          </div>
        {/each}
      </div>
      <p class="text-xs text-gray-500 mt-1">Add multiple interfaces separated by commas</p>
    </div>
    
    <!-- Access Points (Array) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Access Points</label>
      <div class="space-y-2">
        {#each component.access_points as point, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              bind:value={component.access_points[index]}
              on:input={() => component.access_points = updateItem(component.access_points, index, component.access_points[index])}
              class="flex-1 rounded-md"
              placeholder="OBD-II, Debug Port, etc."
            />
            {#if index === component.access_points.length - 1}
              <button 
                type="button"
                on:click={() => component.access_points = addItem(component.access_points)}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.access_points = removeItem(component.access_points, index)}
                class="p-2 bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 rounded-md transition-colors"
              >
                <Trash2 size={16} />
              </button>
            {/if}
          </div>
        {/each}
      </div>
    </div>
    
    <!-- Data Types (Array) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Data Types</label>
      <div class="space-y-2">
        {#each component.data_types as dataType, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              bind:value={component.data_types[index]}
              on:input={() => component.data_types = updateItem(component.data_types, index, component.data_types[index])}
              class="flex-1 rounded-md"
              placeholder="Control Commands, Sensor Data, etc."
            />
            {#if index === component.data_types.length - 1}
              <button 
                type="button"
                on:click={() => component.data_types = addItem(component.data_types)}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.data_types = removeItem(component.data_types, index)}
                class="p-2 bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 rounded-md transition-colors"
              >
                <Trash2 size={16} />
              </button>
            {/if}
          </div>
        {/each}
      </div>
    </div>
    
    <!-- Connected To (Array of Select) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Connected To</label>
      <div class="space-y-2">
        {#each component.connected_to as connected, index}
          <div class="flex gap-2">
            <select 
              bind:value={component.connected_to[index]}
              on:change={() => component.connected_to = updateItem(component.connected_to, index, component.connected_to[index])}
              class="flex-1 rounded-md">
              <option value="">Select a component</option>
              {#each availableComponents.filter(c => c.component_id !== component.component_id) as avComp}
                <option value={avComp.component_id}>{avComp.name} ({avComp.component_id})</option>
              {/each}
            </select>
            
            {#if index === component.connected_to.length - 1}
              <button 
                type="button"
                on:click={() => component.connected_to = addItem(component.connected_to)}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.connected_to = removeItem(component.connected_to, index)}
                class="p-2 bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 rounded-md transition-colors"
              >
                <Trash2 size={16} />
              </button>
            {/if}
          </div>
        {/each}
      </div>
      <p class="text-xs text-gray-500 mt-1">Select components this component is connected to</p>
    </div>
    
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <button 
        type="button"
        on:click={handleCancel} 
        class="btn px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
        Cancel
      </button>
      <button 
        type="submit"
        class="btn btn-primary flex items-center gap-2">
        <Save size={16} />
        {editMode ? 'Update Component' : 'Save Component'}
      </button>
    </div>
  </form>
</div>
