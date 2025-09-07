<script lang="ts">
  import type { APIError } from '$lib/utils/errorHandler';
  import { getErrorMessage, hasFieldErrors } from '$lib/utils/errorHandler';
  
  export let error: APIError | null = null;
  export let showRetry: boolean = false;
  export let onRetry: (() => void) | null = null;
  export let dismissible: boolean = true;
  export let onDismiss: (() => void) | null = null;
  
  function handleRetry() {
    if (onRetry) onRetry();
  }
  
  function handleDismiss() {
    if (onDismiss) onDismiss();
  }
  
  $: errorMessage = error ? getErrorMessage(error) : '';
  $: showFieldErrors = error ? hasFieldErrors(error) : false;
</script>

{#if error}
  <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
    <div class="flex items-start">
      <div class="flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
      </div>
      
      <div class="ml-3 flex-1">
        <h3 class="text-sm font-medium text-red-800">
          {errorMessage}
        </h3>
        
        {#if showFieldErrors && error.field_errors}
          <div class="mt-2">
            <ul class="list-disc list-inside text-sm text-red-700">
              {#each Object.entries(error.field_errors) as [field, message]}
                <li><span class="font-medium">{field}:</span> {message}</li>
              {/each}
            </ul>
          </div>
        {/if}
        
        {#if error.valid_types}
          <div class="mt-2">
            <p class="text-sm text-red-700">
              Valid options: {error.valid_types.join(', ')}
            </p>
          </div>
        {/if}
        
        <div class="mt-3 flex space-x-2">
          {#if showRetry && onRetry}
            <button
              type="button"
              class="bg-red-100 px-3 py-1 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500"
              on:click={handleRetry}
            >
              Try Again
            </button>
          {/if}
          
          {#if dismissible && onDismiss}
            <button
              type="button"
              class="bg-red-100 px-3 py-1 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500"
              on:click={handleDismiss}
            >
              Dismiss
            </button>
          {/if}
        </div>
      </div>
      
      {#if dismissible && onDismiss}
        <div class="ml-auto pl-3">
            <button
              type="button"
              class="inline-flex text-red-400 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
              on:click={handleDismiss}
              aria-label="Close error message"
            >
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
