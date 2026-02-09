<script lang="ts">
  import { Package, Shield, FileText } from '@lucide/svelte';
</script>

<div class="mt-6 rounded-lg p-5" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
  <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Next Steps</h3>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <a
      href="/assets"
      class="flex items-center p-3 rounded-lg transition-colors" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
    >
      <Package class="w-4 h-4 mr-3" style="color: var(--color-accent-primary);" />
      <div>
        <div class="text-xs font-medium" style="color: var(--color-text-primary);">Manage Assets</div>
        <div class="text-[10px]" style="color: var(--color-text-tertiary);">Add system components</div>
      </div>
    </a>

    <a
      href="/damage-scenarios"
      class="flex items-center p-3 rounded-lg transition-colors" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
    >
      <Shield class="w-4 h-4 mr-3" style="color: var(--color-accent-primary);" />
      <div>
        <div class="text-xs font-medium" style="color: var(--color-text-primary);">Damage Scenarios</div>
        <div class="text-[10px]" style="color: var(--color-text-tertiary);">Define potential damages</div>
      </div>
    </a>

    <a
      href="/reports"
      class="flex items-center p-3 rounded-lg transition-colors" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
    >
      <FileText class="w-4 h-4 mr-3" style="color: var(--color-accent-primary);" />
      <div>
        <div class="text-xs font-medium" style="color: var(--color-text-primary);">Generate Report</div>
        <div class="text-[10px]" style="color: var(--color-text-tertiary);">Export analysis results</div>
      </div>
    </a>
  </div>
</div>
