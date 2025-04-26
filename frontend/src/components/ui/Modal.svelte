<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  
  export let title: string = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
  
  const dispatch = createEventDispatcher();
  
  // Close modal on escape key
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      dispatch('close');
    }
  }
  
  // Size classes for modal width
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };
  
  // Add keydown event listener on mount, remove on destroy
  onDestroy(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
  
  window.addEventListener('keydown', handleKeydown);
</script>

<div class="fixed inset-0 z-50 overflow-y-auto" 
     aria-labelledby="modal-title" 
     role="dialog" 
     aria-modal="true"
     transition:fade={{ duration: 150 }}>
  <div class="flex items-center justify-center min-h-screen p-4 text-center sm:p-0">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" 
         on:click={() => dispatch('close')}
         aria-hidden="true"></div>
    
    <!-- Modal panel -->
    <div class="relative inline-block w-full {sizeClasses[size]} p-4 my-8 overflow-hidden text-left 
                align-middle bg-white rounded-lg shadow-xl transform transition-all"
         transition:fly={{ y: 20, duration: 300 }}>
      
      <!-- Header -->
      {#if title}
        <div class="pb-3 border-b">
          <h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">
            {title}
          </h3>
          
          <button 
            type="button"
            class="absolute top-4 right-4 text-gray-400 hover:text-gray-500"
            on:click={() => dispatch('close')}
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      {/if}
      
      <!-- Content -->
      <div>
        <slot></slot>
      </div>
    </div>
  </div>
</div>
