<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { CheckCircle, AlertCircle, X, Info, AlertTriangle } from '@lucide/svelte';

  export let type: 'success' | 'error' | 'info' | 'warning' = 'info';
  export let message: string;
  export let duration: number = 5000; // Default 5 seconds
  export let id: string;

  const dispatch = createEventDispatcher();
  let progressWidth = 100;
  let intervalId: number;

  // Type-specific styling
  $: bgColor = type === 'success' ? 'bg-green-50' 
    : type === 'error' ? 'bg-red-50'
    : type === 'warning' ? 'bg-amber-50'
    : 'bg-blue-50';

  $: borderColor = type === 'success' ? 'border-green-400' 
    : type === 'error' ? 'border-red-400'
    : type === 'warning' ? 'border-amber-400'
    : 'border-blue-400';

  $: textColor = type === 'success' ? 'text-green-800' 
    : type === 'error' ? 'text-red-800'
    : type === 'warning' ? 'text-amber-800'
    : 'text-blue-800';

  $: progressColor = type === 'success' ? 'bg-green-400' 
    : type === 'error' ? 'bg-red-400'
    : type === 'warning' ? 'bg-amber-400'
    : 'bg-blue-400';

  $: icon = type === 'success' ? CheckCircle
    : type === 'error' ? AlertCircle
    : type === 'warning' ? AlertTriangle
    : Info;

  onMount(() => {
    // Start the auto-dismiss timer
    if (duration > 0) {
      const startTime = Date.now();
      const endTime = startTime + duration;
      
      intervalId = window.setInterval(() => {
        const now = Date.now();
        const remaining = Math.max(0, endTime - now);
        progressWidth = (remaining / duration) * 100;
        
        if (remaining <= 0) {
          clearInterval(intervalId);
          close();
        }
      }, 50);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  });

  function close() {
    if (intervalId) clearInterval(intervalId);
    dispatch('dismiss', { id });
  }
</script>

<div 
  class="w-full shadow-xl rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5 {bgColor} border-l-4 {borderColor} animate-slideIn"
  role="alert"
>
  <div class="flex-1 p-4 w-0">
    <div class="flex items-start">
      <div class="flex-shrink-0 mt-0.5">
        <svelte:component this={icon} size={20} class={textColor} />
      </div>
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium {textColor}">{message}</p>
      </div>
    </div>
  </div>
  <div class="flex border-l border-gray-200">
    <button
      on:click={close}
      class="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-600 hover:text-gray-500 focus:outline-none"
    >
      <X size={20} />
    </button>
  </div>
  
  <!-- Progress bar -->
  {#if duration > 0}
    <div class="absolute bottom-0 left-0 h-1 {progressColor}" style="width: {progressWidth}%; transition: width 0.1s linear"></div>
  {/if}
</div>

<style>
  /* Animation for toast entry */
  @keyframes slideIn {
    0% {
      transform: translateX(120%);
      opacity: 0;
    }
    15% {
      transform: translateX(-5%);
    }
    30% {
      transform: translateX(2%);
    }
    45% {
      transform: translateX(-1%);
    }
    60% {
      transform: translateX(0%);
    }
    75% {
      opacity: 1;
    }
    100% {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  .animate-slideIn {
    animation: slideIn 0.5s ease-out forwards;
  }
</style>
