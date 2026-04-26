<script lang="ts">
  import { createEventDispatcher, tick } from 'svelte';
  import { X } from '@lucide/svelte';

  export let isOpen = false;
  export let title = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';

  const dispatch = createEventDispatcher<{
    close: void;
  }>();

  let dialogEl: HTMLDivElement | null = null;
  let triggerEl: HTMLElement | null = null;

  function closeModal() {
    isOpen = false;
    dispatch('close');
    triggerEl?.focus();
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && isOpen) {
      event.stopPropagation();
      closeModal();
    }
    if (event.key === 'Tab' && dialogEl) {
      trapFocus(event);
    }
  }

  function trapFocus(event: KeyboardEvent) {
    const focusable = dialogEl!.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey) {
      if (document.activeElement === first) { event.preventDefault(); last?.focus(); }
    } else {
      if (document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  }

  $: if (isOpen) {
    triggerEl = document.activeElement as HTMLElement;
    tick().then(() => dialogEl?.focus());
  }

  $: sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(0,0,0,0.6);"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
    tabindex="-1"
    bind:this={dialogEl}
  >
    <div
      class="relative w-full {sizeClasses[size]} rounded-lg transform transition-all"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);"
    >
      <div class="flex items-center justify-between p-5" style="border-bottom: 1px solid var(--color-border-subtle);">
        <h2 id="modal-title" class="text-sm font-semibold" style="color: var(--color-text-primary);">
          {title}
        </h2>
        <button
          type="button"
          class="transition-colors"
          style="color: var(--color-text-tertiary);"
          on:click={closeModal}
          aria-label="Close modal"
        >
          <X size={18} />
        </button>
      </div>

      <div class="p-5">
        <slot />
      </div>

      {#if $$slots.footer}
        <div class="flex justify-end gap-2 p-5" style="border-top: 1px solid var(--color-border-subtle);">
          <slot name="footer" />
        </div>
      {/if}
    </div>
  </div>
{/if}
