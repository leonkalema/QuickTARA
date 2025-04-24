<script lang="ts">
  import { Shield, AlertTriangle, Settings, Edit, Trash2, Info } from 'lucide-svelte';
  
  export let component: {
    component_id: string;
    name: string;
    type: string;
    safety_level: string;
    interfaces: string[];
    trust_zone: string;
    location: string;
  };

  // Map trust zone to visual indication
  const getTrustZoneClass = (zone: string): string => {
    switch (zone.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'boundary':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'standard':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'untrusted':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Map safety level to badge class
  const getSafetyLevelClass = (level: string): string => {
    if (level.includes('D')) return 'badge-high';
    if (level.includes('C')) return 'bg-orange-100 text-orange-800';
    if (level.includes('B')) return 'bg-yellow-100 text-yellow-800';
    if (level.includes('A')) return 'badge-low';
    return 'bg-gray-100 text-gray-800';
  };

  // Get icon based on component type
  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'ecu':
        return Settings;
      case 'sensor':
        return AlertTriangle;
      case 'gateway':
        return Shield;
      default:
        return Settings;
    }
  };

  const Icon = getTypeIcon(component.type);

  // Event handlers
  function handleEdit() {
    dispatch('edit', component);
  }
  
  function handleDelete() {
    dispatch('delete', component.component_id);
  }
  
  function handleDetails() {
    dispatch('details', component);
  }
  
  // Create a dispatch function for events
  function dispatch(name: string, detail: any) {
    const event = new CustomEvent(name, { detail });
    dispatchEvent(event);
  }
</script>

<div class="bg-white rounded-xl shadow-sm p-4 hover:shadow transition-shadow duration-200 border border-gray-100">
  <div class="flex justify-between items-start">
    <div class="flex gap-3">
      <div class="p-2 rounded-lg {getTrustZoneClass(component.trust_zone)}">
        <Icon size={20} />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900">{component.name}</h3>
        <p class="text-sm text-gray-500 mt-0.5">{component.component_id}</p>
      </div>
    </div>
    <span class={`text-xs font-medium px-2 py-1 rounded-full ${getSafetyLevelClass(component.safety_level)}`}>
      {component.safety_level}
    </span>
  </div>
  
  <div class="mt-4 flex flex-wrap gap-2">
    {#each component.interfaces as interface}
      <span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{interface}</span>
    {/each}
  </div>
  
  <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
    <div class="flex items-center">
      <span class="text-sm font-medium {getTrustZoneClass(component.trust_zone)} px-2 py-1 rounded">
        {component.trust_zone}
      </span>
      <span class="text-sm text-gray-500 ml-2">{component.location}</span>
    </div>
    <div class="flex space-x-2">
      <button 
        on:click={handleDetails}
        class="p-1.5 text-primary hover:bg-blue-50 rounded-full transition-colors">
        <Info size={18} />
      </button>
      <button 
        on:click={handleEdit}
        class="p-1.5 text-primary hover:bg-blue-50 rounded-full transition-colors">
        <Edit size={18} />
      </button>
      <button 
        on:click={handleDelete}
        class="p-1.5 text-danger hover:bg-red-50 rounded-full transition-colors">
        <Trash2 size={18} />
      </button>
    </div>
  </div>
</div>
