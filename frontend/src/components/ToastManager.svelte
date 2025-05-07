<script lang="ts" context="module">
  import { writable } from 'svelte/store';
  
  // Create a store for toast notifications
  const toasts = writable<{
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    duration: number;
  }[]>([]);
  
  // Helper functions to add different types of toasts
  export function showSuccess(message: string, duration = 5000) {
    addToast('success', message, duration);
  }
  
  export function showError(message: string, duration = 5000) {
    addToast('error', message, duration);
  }
  
  export function showInfo(message: string, duration = 5000) {
    addToast('info', message, duration);
  }
  
  export function showWarning(message: string, duration = 5000) {
    addToast('warning', message, duration);
  }
  
  function addToast(type: 'success' | 'error' | 'info' | 'warning', message: string, duration: number) {
    const id = Date.now().toString();
    toasts.update(all => [...all, { id, type, message, duration }]);
  }
  
  export function dismissToast(id: string) {
    toasts.update(all => all.filter(t => t.id !== id));
  }
</script>

<script lang="ts">
  import Toast from './Toast.svelte';
</script>

<div class="fixed top-0 right-0 mt-16 p-4 z-[1000] flex flex-col space-y-3 items-end max-w-md w-full">
  {#each $toasts as toast (toast.id)}
    <Toast 
      id={toast.id}
      type={toast.type}
      message={toast.message}
      duration={toast.duration}
      on:dismiss={e => dismissToast(e.detail.id)}
    />
  {/each}
</div>
