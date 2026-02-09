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

  $: variantStyles = {
    danger: { iconColor: 'var(--color-error)', btnBg: 'var(--color-error)' },
    warning: { iconColor: 'var(--color-warning)', btnBg: 'var(--color-warning)' },
    info: { iconColor: 'var(--color-info)', btnBg: 'var(--color-accent-primary)' }
  };
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(0,0,0,0.6);"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    aria-labelledby="confirmation-title"
    tabindex="-1"
  >
    <div
      class="relative w-full max-w-md rounded-lg transform transition-all"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);"
    >
      <div class="flex items-center justify-between p-5" style="border-bottom: 1px solid var(--color-border-subtle);">
        <div class="flex items-center gap-3">
          <AlertTriangle size={20} style="color: {variantStyles[variant].iconColor};" />
          <h2 id="confirmation-title" class="text-sm font-semibold" style="color: var(--color-text-primary);">
            {title}
          </h2>
        </div>
        <button
          type="button"
          class="transition-colors"
          style="color: var(--color-text-tertiary);"
          on:click={handleCancel}
          aria-label="Close modal"
          disabled={isLoading}
        >
          <X size={18} />
        </button>
      </div>

      <div class="p-5">
        <p class="text-sm leading-relaxed" style="color: var(--color-text-secondary);">
          {message}
        </p>
      </div>

      <div class="flex justify-end gap-2 p-5" style="border-top: 1px solid var(--color-border-subtle);">
        <button
          type="button"
          class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
          style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
          on:click={handleCancel}
          disabled={isLoading}
        >
          {cancelText}
        </button>
        <button
          type="button"
          class="px-3 py-2 text-sm font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          style="background: {variantStyles[variant].btnBg}; color: var(--color-text-inverse);"
          on:click={handleConfirm}
          disabled={isLoading}
        >
          {#if isLoading}
            <div class="flex items-center gap-2">
              <div class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
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
