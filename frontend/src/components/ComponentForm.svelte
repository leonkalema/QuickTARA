<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Save, Plus, Trash2 } from '@lucide/svelte';
  import SecurityPropertiesWizard from './SecurityPropertiesWizard.svelte';
  import { scopeApi, type SystemScope } from '../api/scope';
  import { safeApiCall } from '../utils/error-handler';
  
  // Default component types and safety levels
  const componentTypes = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network'];
  const safetyLevels = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D'];
  const trustZones = ['Critical', 'Boundary', 'Standard', 'Untrusted'];
  const locations = ['Internal', 'External'];
  
  // Define component type
  type ComponentType = {
    component_id: string;
    name: string;
    type: string;
    safety_level: string;
    interfaces: string[];
    access_points: string[];
    data_types: string[];
    location: string;
    trust_zone: string;
    connected_to: string[];
    scope_id: string;
    // Security properties
    confidentiality: string;
    integrity: string;
    availability: string;
    authenticity_required: boolean;
    authorization_required: boolean;
    [key: string]: string | string[] | boolean;
  };
  
  // Component input
  export let editMode = false;
  export let viewMode = false;
  export let component: ComponentType = {
    component_id: '',
    name: '',
    type: componentTypes[0],
    safety_level: safetyLevels[0],
    interfaces: [''],
    access_points: [''],
    data_types: [''],
    location: locations[0],
    trust_zone: trustZones[0],
    connected_to: [''],
    scope_id: '',
    // Security properties
    confidentiality: 'Medium',
    integrity: 'Medium',
    availability: 'Medium',
    authenticity_required: false,
    authorization_required: false
  };
  
  // Available components for connection selection
  export let availableComponents: { component_id: string; name: string; }[] = [];
  
  // Available scopes for selection
  let availableScopes: SystemScope[] = [];
  
  const dispatch = createEventDispatcher();
  
  // Load available scopes
  onMount(async () => {
    const result = await safeApiCall(scopeApi.getAll);
    if (result) {
      availableScopes = result.scopes;
    }
  });
  
  // Form validation
  let validationErrors: { [key: string]: string } = {};
  
  function validateForm(): boolean {
    validationErrors = {};
    
    // Component ID validation (only for new components)
    if (!editMode) {
      if (!component.component_id) {
        validationErrors.component_id = 'Component ID is required';
      } else if (!/^[A-Za-z0-9_-]+$/.test(component.component_id)) {
        validationErrors.component_id = 'Component ID can only contain letters, numbers, underscores, and hyphens';
      } else if (availableComponents.some(c => c.component_id === component.component_id)) {
        validationErrors.component_id = 'Component ID already exists';
      }
    }
    
    // Name validation
    if (!component.name.trim()) {
      validationErrors.name = 'Name is required';
    }
    
    // Required field validation
    if (!component.type) {
      validationErrors.type = 'Type is required';
    }
    
    if (!component.safety_level) {
      validationErrors.safety_level = 'Safety level is required';
    }
    
    if (!component.trust_zone) {
      validationErrors.trust_zone = 'Trust zone is required';
    }
    
    // Check for empty arrays
    if (component.interfaces.length === 0 || (component.interfaces.length === 1 && !component.interfaces[0])) {
      validationErrors.interfaces = 'At least one interface is required';
    }
    
    return Object.keys(validationErrors).length === 0;
  }
  
  // Map wizard-selected values to backend enum strings (Title-case / "N/A")
  function normalizeSecurityLevel(level: string): string {
    switch (level?.toUpperCase()) {
      case 'HIGH':
        return 'High';
      case 'MEDIUM':
        return 'Medium';
      case 'LOW':
        return 'Low';
      case 'NOT_APPLICABLE':
        return 'N/A';
      default:
        return level;
    }
  }
  
  function handleSubmit() {
    // Validate the form
    if (!validateForm()) {
      return; // Stop if validation fails
    }
    
    // Normalize and deduplicate array values
    const normalizeArray = (arr: string[]) => {
      return [...new Set(arr
        .filter(i => i.trim() !== '')
        .map(i => i.trim())
      )];
    };
    
    // Clean and normalize the component data
    const cleanedComponent = {
      ...component,
      // Normalize ID and name
      component_id: component.component_id.trim(),
      name: component.name.trim(),
      // Convert security level strings to backend accepted values
      confidentiality: normalizeSecurityLevel(component.confidentiality as string),
      integrity: normalizeSecurityLevel(component.integrity as string),
      availability: normalizeSecurityLevel(component.availability as string),
      // Include scope ID only if provided
      scope_id: component.scope_id || undefined,
      // Normalize and deduplicate arrays
      interfaces: normalizeArray(component.interfaces),
      access_points: normalizeArray(component.access_points),
      data_types: normalizeArray(component.data_types),
      connected_to: normalizeArray(component.connected_to)
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

<div class="bg-white rounded-xl shadow-lg p-6 max-w-2xl mx-auto border border-gray-100 {viewMode ? 'view-mode' : ''}">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        {#if viewMode}
          View Component
        {:else if editMode}
          Edit Component
        {:else}
          Add New Component
        {/if}
      </h2>
      {#if viewMode}
        <p class="text-sm text-gray-500 mt-1">Read-only view</p>
      {/if}
    </div>
    <button 
      on:click={handleCancel}
      class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
      <X size={20} />
    </button>
  </div>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">    
      <!-- Scope Selection -->
      <div class="col-span-2">
        <label for="scope_id" class="block text-sm font-medium text-gray-700 mb-1">System Scope</label>
        <select 
          id="scope_id" 
          bind:value={component.scope_id}
          class="w-full rounded-md"
          disabled={viewMode}
        >
          <option value="">-- No Scope Selected --</option>
          {#each availableScopes as scope}
            <option value={scope.scope_id}>{scope.name} ({scope.system_type})</option>
          {/each}
        </select>
        <p class="text-xs text-gray-500 mt-1">Associate this component with a defined system scope</p>
      </div>
      <!-- Component ID -->
      <div>
        <label for="component_id" class="block text-sm font-medium {validationErrors.component_id ? 'text-red-700' : 'text-gray-700'} mb-1">Component ID *</label>
        <input 
          type="text" 
          id="component_id" 
          bind:value={component.component_id}
          placeholder="component-001"
          disabled={viewMode || editMode}
          class="w-full rounded-md {validationErrors.component_id ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}"
        />
        {#if validationErrors.component_id}
          <p class="text-xs text-red-600 mt-1">{validationErrors.component_id}</p>
        {/if}
      </div>
      
      <!-- Name -->
      <div>
        <label for="name" class="block text-sm font-medium {validationErrors.name ? 'text-red-700' : 'text-gray-700'} mb-1">Name *</label>
        <input 
          type="text" 
          id="name" 
          bind:value={component.name}
          disabled={viewMode}
          required
          class="w-full rounded-md {validationErrors.name ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}"
          placeholder="Engine Control Unit"
        />
        {#if validationErrors.name}
          <p class="text-xs text-red-600 mt-1">{validationErrors.name}</p>
        {/if}
      </div>
      
      <!-- Type -->
      <div>
        <label for="type" class="block text-sm font-medium {validationErrors.type ? 'text-red-700' : 'text-gray-700'} mb-1">Type *</label>
        <select 
          id="type" 
          bind:value={component.type}
          disabled={viewMode}
          required
          class="w-full rounded-md {validationErrors.type ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}">
          <option value="" disabled>Select a type</option>
          {#each componentTypes as type}
            <option value={type}>{type}</option>
          {/each}
        </select>
        {#if validationErrors.type}
          <p class="text-xs text-red-600 mt-1">{validationErrors.type}</p>
        {/if}
      </div>
      
      <!-- Safety Level -->
      <div>
        <label for="safety_level" class="block text-sm font-medium {validationErrors.safety_level ? 'text-red-700' : 'text-gray-700'} mb-1">Safety Level *</label>
        <select 
          id="safety_level" 
          bind:value={component.safety_level}
          disabled={viewMode}
          required
          class="w-full rounded-md {validationErrors.safety_level ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}">
          <option value="" disabled>Select safety level</option>
          {#each safetyLevels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
        {#if validationErrors.safety_level}
          <p class="text-xs text-red-600 mt-1">{validationErrors.safety_level}</p>
        {/if}
      </div>
      
      <!-- Location -->
      <div>
        <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location *</label>
        <select 
          id="location" 
          bind:value={component.location}
          disabled={viewMode}
          required
          class="w-full rounded-md">
          {#each locations as location}
            <option value={location}>{location}</option>
          {/each}
        </select>
      </div>
      
      <!-- Trust Zone -->
      <div>
        <label for="trust_zone" class="block text-sm font-medium {validationErrors.trust_zone ? 'text-red-700' : 'text-gray-700'} mb-1">Trust Zone *</label>
        <select 
          id="trust_zone" 
          bind:value={component.trust_zone}
          disabled={viewMode}
          required
          class="w-full rounded-md {validationErrors.trust_zone ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}">
          <option value="" disabled>Select trust zone</option>
          {#each trustZones as zone}
            <option value={zone}>{zone}</option>
          {/each}
        </select>
        {#if validationErrors.trust_zone}
          <p class="text-xs text-red-600 mt-1">{validationErrors.trust_zone}</p>
        {/if}
      </div>
    </div>
    
    <!-- Interfaces (Array) -->
    <div>
      <div class="flex justify-between items-center mb-2">
        <label for="interfaces-group" class="block text-sm font-medium {validationErrors.interfaces ? 'text-red-700' : 'text-gray-700'}">Interfaces *</label>
      </div>
      <div id="interfaces-group" class="space-y-2" role="group" aria-labelledby="interfaces-label">
        {#each component.interfaces as interfaceItem, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              id={`interface-${index}`}
              bind:value={component.interfaces[index]}
              disabled={viewMode}
              on:input={() => component.interfaces = updateItem(component.interfaces, index, component.interfaces[index])}
              class="flex-1 rounded-md {validationErrors.interfaces ? 'border-red-300 ring-red-200 focus:border-red-500 focus:ring-red-200' : ''}"
              placeholder="CAN, Ethernet, etc."
              aria-label={`Interface ${index + 1}`}
            />
            {#if index === component.interfaces.length - 1}
              <button 
                type="button"
                on:click={() => component.interfaces = addItem(component.interfaces)}
                disabled={viewMode}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.interfaces = removeItem(component.interfaces, index)}
                disabled={viewMode}
                class="p-2 bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 rounded-md transition-colors"
              >
                <Trash2 size={16} />
              </button>
            {/if}
          </div>
        {/each}
      </div>
      <p class="text-xs text-gray-500 mt-1">Add multiple interfaces separated by commas</p>
      {#if validationErrors.interfaces}
        <p class="text-xs text-red-600 mt-1">{validationErrors.interfaces}</p>
      {/if}
    </div>
    
    <!-- Access Points (Array) -->
    <div>
      <div class="flex justify-between items-center mb-2">
        <label for="access-points-group" class="block text-sm font-medium text-gray-700">Access Points</label>
      </div>
      <div id="access-points-group" class="space-y-2" role="group" aria-labelledby="access-points-label">
        {#each component.access_points as point, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              id={`access-point-${index}`}
              bind:value={component.access_points[index]}
              disabled={viewMode}
              on:input={() => component.access_points = updateItem(component.access_points, index, component.access_points[index])}
              class="flex-1 rounded-md"
              placeholder="OBD Port, USB, etc."
              aria-label={`Access Point ${index + 1}`}
            />
            {#if index === component.access_points.length - 1}
              <button 
                type="button"
                on:click={() => component.access_points = addItem(component.access_points)}
                disabled={viewMode}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.access_points = removeItem(component.access_points, index)}
                disabled={viewMode}
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
      <div class="flex justify-between items-center mb-2">
        <label for="data-types-group" class="block text-sm font-medium text-gray-700">Data Types</label>
      </div>
      <div id="data-types-group" class="space-y-2" role="group" aria-labelledby="data-types-label">
        {#each component.data_types as dataType, index}
          <div class="flex gap-2">
            <input 
              type="text" 
              id={`data-type-${index}`}
              bind:value={component.data_types[index]}
              disabled={viewMode}
              on:input={() => component.data_types = updateItem(component.data_types, index, component.data_types[index])}
              class="flex-1 rounded-md"
              placeholder="Control Commands, Sensor Data, etc."
              aria-label={`Data Type ${index + 1}`}
            />
            {#if index === component.data_types.length - 1}
              <button 
                type="button"
                on:click={() => component.data_types = addItem(component.data_types)}
                disabled={viewMode}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.data_types = removeItem(component.data_types, index)}
                disabled={viewMode}
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
      <div class="flex justify-between items-center mb-2">
        <label for="connected-to-group" class="block text-sm font-medium text-gray-700">Connected To</label>
      </div>
      <div id="connected-to-group" class="space-y-2" role="group" aria-labelledby="connected-to-label">
        {#each component.connected_to as connected, index}
          <div class="flex gap-2">
            <select 
              id={`connected-to-${index}`}
              bind:value={component.connected_to[index]}
              disabled={viewMode}
              on:change={() => component.connected_to = updateItem(component.connected_to, index, component.connected_to[index])}
              class="flex-1 rounded-md"
              aria-label={`Connected Component ${index + 1}`}>
              <option value="">Select a component</option>
              {#each availableComponents.filter(c => c.component_id !== component.component_id) as avComp}
                <option value={avComp.component_id}>{avComp.name} ({avComp.component_id})</option>
              {/each}
            </select>
            
            {#if index === component.connected_to.length - 1}
              <button 
                type="button"
                on:click={() => component.connected_to = addItem(component.connected_to)}
                disabled={viewMode}
                class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
              >
                <Plus size={16} />
              </button>
            {:else}
              <button 
                type="button"
                on:click={() => component.connected_to = removeItem(component.connected_to, index)}
                disabled={viewMode}
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
    
    <!-- Security Properties Wizard -->
    <div>
      <h3 class="text-sm font-medium text-gray-700 mb-2">Security Properties</h3>
      <SecurityPropertiesWizard 
        values={{
          confidentiality: component.confidentiality,
          integrity: component.integrity,
          availability: component.availability,
          authenticity_required: component.authenticity_required,
          authorization_required: component.authorization_required
        }}
        onChange={(property, value) => {
          component[property] = value;
        }}
        readOnly={viewMode}
      />
    </div>
    
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <button 
        type="button"
        on:click={handleCancel} 
        class="btn px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
        {viewMode ? 'Close' : 'Cancel'}
      </button>
      
      {#if !viewMode}
        <button 
          type="submit"
          class="btn btn-primary flex items-center gap-2" 
          disabled={Object.keys(validationErrors).length > 0}>
          <Save size={16} />
          {editMode ? 'Update Component' : 'Save Component'}
        </button>
      {/if}
    </div>
  </form>
</div>
