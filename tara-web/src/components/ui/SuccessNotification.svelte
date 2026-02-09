<script lang="ts">
  import { onMount } from 'svelte';
  import { Check, X } from '@lucide/svelte';

  export let message: string = '';
  export let show: boolean = false;
  export let duration: number = 3000;
  export let type: 'success' | 'info' | 'warning' | 'error' = 'success';

  let visible = false;
  let timeoutId: number;

  $: if (show) {
    visible = true;
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      visible = false;
      show = false;
    }, duration);
  }

  function close() {
    visible = false;
    show = false;
    clearTimeout(timeoutId);
  }

  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800'
  };

  const iconStyles = {
    success: 'text-green-600',
    info: 'text-blue-600',
    warning: 'text-yellow-600',
    error: 'text-red-600'
  };
</script>

{#if visible}
  <div class="fixed top-4 right-4 z-50 max-w-sm w-full">
    <div class="border rounded-lg p-4 shadow-lg transition-all duration-300 {typeStyles[type]}">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <Check class="w-5 h-5 {iconStyles[type]}" />
        </div>
        <div class="ml-3 flex-1">
          <p class="text-sm font-medium">
            {message}
          </p>
        </div>
        <div class="ml-4 flex-shrink-0">
          <button
            class="inline-flex rounded-md p-1.5 hover:opacity-80 focus:outline-none"
            on:click={close}
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
