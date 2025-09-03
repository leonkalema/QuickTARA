<script lang="ts">
  import { notifications } from '../../lib/stores/notificationStore';
  import { Check, Info, AlertTriangle, X as XIcon } from '@lucide/svelte';

  function getIcon(type: string) {
    switch (type) {
      case 'success': return Check;
      case 'info': return Info;
      case 'warning': return AlertTriangle;
      case 'error': return XIcon;
      default: return Check;
    }
  }

  function getStyles(type: string) {
    switch (type) {
      case 'success': return 'bg-green-50 border-green-200 text-green-800';
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-green-50 border-green-200 text-green-800';
    }
  }

  function getIconStyles(type: string) {
    switch (type) {
      case 'success': return 'text-green-600';
      case 'info': return 'text-blue-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-green-600';
    }
  }
</script>

<div class="fixed top-4 right-4 z-50 space-y-2">
  {#each $notifications as notification (notification.id)}
    <div class="max-w-sm w-full animate-slide-in">
      <div class="border rounded-lg p-4 shadow-lg {getStyles(notification.type)}">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svelte:component this={getIcon(notification.type)} class="w-5 h-5 {getIconStyles(notification.type)}" />
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium">
              {notification.message}
            </p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              class="inline-flex rounded-md p-1.5 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-offset-2"
              on:click={() => notifications.remove(notification.id)}
            >
              <XIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  @keyframes slide-in {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .animate-slide-in {
    animation: slide-in 0.3s ease-out;
  }
</style>
