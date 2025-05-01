<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  export let id: string = '';
  export let label: string = '';
  export let options: { value: string; label: string; selected?: boolean }[] = [];
  export let selectedValues: string[] = [];
  export let placeholder: string = 'Select options';
  export let disabled: boolean = false;
  export let maxHeight: string = '250px';

  const dispatch = createEventDispatcher();
  let isOpen = false;
  let dropdownElement: HTMLDivElement;

  $: selectedOptions = options.filter(option => selectedValues.includes(option.value));
  
  // Handle clicks outside the dropdown to close it
  function handleClickOutside(event: MouseEvent) {
    if (dropdownElement && !dropdownElement.contains(event.target as Node)) {
      isOpen = false;
    }
  }

  // Toggle selection of an option
  function toggleOption(value: string) {
    if (selectedValues.includes(value)) {
      selectedValues = selectedValues.filter(v => v !== value);
    } else {
      selectedValues = [...selectedValues, value];
    }
    dispatch('change', selectedValues);
  }

  // Initialize event listeners
  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<div class="multi-select-container" bind:this={dropdownElement}>
  {#if label}
    <label for={id} class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
  {/if}
  
  <div 
    class="relative"
    class:disabled={disabled}
  >
    <!-- Selected options display / trigger -->
    <div 
      class="flex items-center justify-between w-full p-2.5 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 cursor-pointer"
      on:click={() => isOpen = !isOpen}
      aria-haspopup="listbox"
      aria-expanded={isOpen}
    >
      <div class="flex flex-wrap gap-1">
        {#if selectedOptions.length === 0}
          <span class="text-gray-400">{placeholder}</span>
        {:else}
          {#each selectedOptions as option}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
              {option.label}
            </span>
          {/each}
        {/if}
      </div>
      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isOpen ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"}></path>
      </svg>
    </div>
    
    <!-- Dropdown menu -->
    {#if isOpen}
      <div 
        class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg"
        style="max-height: {maxHeight}; overflow-y: auto;"
      >
        <ul class="py-1" role="listbox" aria-multiselectable="true">
          {#each options as option}
            <li 
              class="px-3 py-2 cursor-pointer hover:bg-gray-100 flex items-center"
              class:bg-gray-50={selectedValues.includes(option.value)}
              role="option"
              aria-selected={selectedValues.includes(option.value)}
              on:click={() => toggleOption(option.value)}
            >
              <input 
                type="checkbox" 
                checked={selectedValues.includes(option.value)} 
                class="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span>{option.label}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</div>

<style>
  .multi-select-container {
    width: 100%;
    margin-bottom: 1rem;
    position: relative;
  }
  
  .disabled {
    opacity: 0.6;
    pointer-events: none;
  }
</style>
