<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Shield, AlertTriangle, Settings, Edit, Trash2, Target, Eye } from '@lucide/svelte';
  import { scopeApi, type SystemScope } from '../api/scope';
  import { safeApiCall } from '../utils/error-handler';
  
  export let component: {
    component_id: string;
    name: string;
    type: string;
    safety_level: string;
    interfaces: string[];
    trust_zone: string;
    location: string;
    scope_id?: string;
  };

  const dispatch = createEventDispatcher();
  
  // Store scope info if available
  let scopeInfo: SystemScope | null = null;
  
  // Load scope information if component has scope_id
  onMount(async () => {
    if (component.scope_id) {
      try {
        scopeInfo = await safeApiCall(() => scopeApi.getById(component.scope_id!));
      } catch (error) {
        console.error('Error loading scope info:', error);
      }
    }
  });

  // Map trust zone to safety level for visual indication
  const getTrustZoneClass = (zone: string): string => {
    switch (zone.toLowerCase()) {
      case 'critical':
        return 'bg-red-50 text-rose-700 border-red-100';
      case 'boundary':
        return 'bg-amber-50 text-amber-700 border-amber-100';
      case 'standard':
        return 'bg-blue-50 text-blue-700 border-blue-100';
      case 'untrusted':
        return 'bg-slate-50 text-slate-700 border-slate-100';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-100';
    }
  };

  // Map safety level to badge class
  const getSafetyLevelClass = (level: string): string => {
    if (level.includes('D')) return 'bg-rose-50 text-rose-700';
    if (level.includes('C')) return 'bg-amber-50 text-amber-700';
    if (level.includes('B')) return 'bg-yellow-50 text-yellow-700';
    if (level.includes('A')) return 'bg-emerald-50 text-emerald-700';
    return 'bg-slate-50 text-slate-700';
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

  // Function to handle view action
  function handleView() {
    // Dispatch view event
    dispatch('view', component);
  }

  // Function to handle edit action
  function handleEdit() {
    // Dispatch edit event
    dispatch('edit', component);
  }
  
  // Function to handle delete action
  function handleDelete() {
    // Dispatch delete event
    dispatch('delete', component.component_id);
  }
</script>

<div style="background-color: var(--color-card-bg); border: 1px solid var(--color-border);" class="rounded-xl shadow-sm p-4 hover:shadow-md transition-all duration-300">
  <div class="flex justify-between items-start">
    <div class="flex gap-3">
      <div class="p-2 rounded-lg {getTrustZoneClass(component.trust_zone)}">
        <Icon size={20} />
      </div>
      <div>
        <h3 class="text-lg font-semibold" style="color: var(--color-text-main);">{component.name}</h3>
        <p class="text-sm mt-0.5" style="color: var(--color-text-muted);">{component.component_id}</p>
      </div>
    </div>
    <span class={`text-xs font-medium px-2 py-1 rounded-full ${getSafetyLevelClass(component.safety_level)}`}>
      {component.safety_level}
    </span>
  </div>
  
  <div class="mt-4 flex flex-wrap gap-2">
    {#each component.interfaces as interfaceItem}
      <span class="text-xs px-2 py-1 rounded" style="background-color: var(--color-background); color: var(--color-text-main); border: 1px solid var(--color-border);">{interfaceItem}</span>
    {/each}
  </div>
  
  <!-- Scope information if available -->
  {#if component.scope_id && scopeInfo}
    <div class="mt-4 p-2 rounded-md flex items-center gap-2" style="background-color: var(--color-background); border: 1px solid var(--color-border);">
      <Target size={14} style="color: var(--color-primary);" />
      <span class="text-xs" style="color: var(--color-text-main);">
        Scope: <span class="font-medium">{scopeInfo.name}</span> ({scopeInfo.system_type})
      </span>
    </div>
  {/if}
  
  <div class="flex justify-between items-center mt-4 pt-3" style="border-top: 1px solid var(--color-border);">
    <span class="text-sm font-medium {getTrustZoneClass(component.trust_zone)} px-2 py-1 rounded">
      {component.trust_zone}
    </span>
    <div class="flex space-x-2">
      <button 
        on:click={handleView}
        class="p-1.5 rounded-full transition-colors" style="color: var(--color-secondary); hover:background-color: rgba(59, 126, 161, 0.1);">
        <Eye size={18} />
      </button>
      <button 
        on:click={handleEdit}
        class="p-1.5 rounded-full transition-colors" style="color: var(--color-primary); hover:background-color: rgba(59, 126, 161, 0.1);">
        <Edit size={18} />
      </button>
      <button 
        on:click={handleDelete}
        class="p-1.5 rounded-full transition-colors" style="color: var(--color-danger); hover:background-color: rgba(208, 83, 83, 0.1);">
        <Trash2 size={18} />
      </button>
    </div>
  </div>
</div>
