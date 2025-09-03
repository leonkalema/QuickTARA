<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { X } from '@lucide/svelte';

  export let isOpen = false;
  export let title = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';

  const dispatch = createEventDispatcher<{
    close: void;
  }>();

  function closeModal() {
    isOpen = false;
    dispatch('close');
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && isOpen) {
      closeModal();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  }

  $: sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
    on:click={handleBackdropClick}
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <div
      class="relative w-full {sizeClasses[size]} bg-white rounded-lg shadow-xl transform transition-all"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 id="modal-title" class="text-xl font-semibold text-gray-900">
          {title}
        </h2>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600 transition-colors"
          on:click={closeModal}
          aria-label="Close modal"
        >
          <X size={24} />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6">
        <slot />
      </div>

      <!-- Footer -->
      {#if $$slots.footer}
        <div class="flex justify-end gap-3 p-6 border-t border-gray-200">
          <slot name="footer" />
        </div>
      {/if}
    </div>
  </div>
{/if}
