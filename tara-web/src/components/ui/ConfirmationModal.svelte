<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { AlertTriangle, X } from '@lucide/svelte';

  export let isOpen = false;
  export let title = 'Confirm Action';
  export let message = 'Are you sure you want to proceed?';
  export let confirmText = 'Confirm';
  export let cancelText = 'Cancel';
  export let variant: 'danger' | 'warning' | 'info' = 'warning';
  export let isLoading = false;

  const dispatch = createEventDispatcher<{
    confirm: void;
    cancel: void;
  }>();

  function handleConfirm() {
    dispatch('confirm');
  }

  function handleCancel() {
    isOpen = false;
    dispatch('cancel');
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && isOpen) {
      handleCancel();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleCancel();
    }
  }

  $: variantClasses = {
    danger: {
      icon: 'text-red-600',
      button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    },
    warning: {
      icon: 'text-yellow-600',
      button: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
    },
    info: {
      icon: 'text-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
    }
  };
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
    on:click={handleBackdropClick}
    role="dialog"
    aria-modal="true"
    aria-labelledby="confirmation-title"
  >
    <div
      class="relative w-full max-w-md bg-white rounded-lg shadow-xl transform transition-all"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <div class="flex items-center gap-3">
          <div class="flex-shrink-0">
            <AlertTriangle size={24} class={variantClasses[variant].icon} />
          </div>
          <h2 id="confirmation-title" class="text-lg font-semibold text-gray-900">
            {title}
          </h2>
        </div>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600 transition-colors"
          on:click={handleCancel}
          aria-label="Close modal"
          disabled={isLoading}
        >
          <X size={20} />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6">
        <p class="text-gray-700 leading-relaxed">
          {message}
        </p>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-3 p-6 border-t border-gray-200">
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          on:click={handleCancel}
          disabled={isLoading}
        >
          {cancelText}
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed {variantClasses[variant].button}"
          on:click={handleConfirm}
          disabled={isLoading}
        >
          {#if isLoading}
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Loading...
            </div>
          {:else}
            {confirmText}
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}
