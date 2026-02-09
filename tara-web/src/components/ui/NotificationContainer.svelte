<script lang="ts">
  import { notifications } from '../../lib/stores/notifications';
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

  interface NotifStyle { bg: string; border: string; fg: string; icon: string }

  function getTokenStyles(type: string): NotifStyle {
    switch (type) {
      case 'success': return { bg: 'var(--color-success-bg)', border: 'var(--color-success)', fg: 'var(--color-success)', icon: 'var(--color-success)' };
      case 'info':    return { bg: 'var(--color-info-bg)',    border: 'var(--color-info)',    fg: 'var(--color-info)',    icon: 'var(--color-info)' };
      case 'warning': return { bg: 'var(--color-warning-bg)', border: 'var(--color-warning)', fg: 'var(--color-warning)', icon: 'var(--color-warning)' };
      case 'error':   return { bg: 'var(--color-error-bg)',   border: 'var(--color-error)',   fg: 'var(--color-error)',   icon: 'var(--color-error)' };
      default:        return { bg: 'var(--color-success-bg)', border: 'var(--color-success)', fg: 'var(--color-success)', icon: 'var(--color-success)' };
    }
  }
</script>

<div class="fixed top-4 right-4 z-50 space-y-2">
  {#each $notifications as notification (notification.id)}
    {@const s = getTokenStyles(notification.type)}
    <div class="max-w-sm w-full animate-slide-in">
      <div
        class="rounded-lg p-3.5"
        style="background: {s.bg}; border: 1px solid {s.border}; box-shadow: var(--shadow-lg);"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svelte:component this={getIcon(notification.type)} class="w-4 h-4" style="color: {s.icon};" />
          </div>
          <div class="ml-2.5 flex-1">
            <p class="text-sm font-medium" style="color: {s.fg};">
              {notification.message}
            </p>
          </div>
          <div class="ml-3 flex-shrink-0">
            <button
              class="inline-flex rounded-md p-1 transition-colors"
              style="color: {s.fg};"
              on:click={() => notifications.remove(notification.id)}
            >
              <XIcon class="w-3.5 h-3.5" />
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
