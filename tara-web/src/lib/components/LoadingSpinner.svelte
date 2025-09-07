<script lang="ts">
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let message: string = 'Loading...';
  export let showMessage: boolean = true;
  
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8', 
    lg: 'w-12 h-12'
  };
</script>

<div class="flex flex-col items-center justify-center p-4">
  <div class="animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 {sizeClasses[size]}"></div>
  {#if showMessage}
    <p class="mt-2 text-sm text-gray-600">{message}</p>
  {/if}
</div>
