<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '$lib/stores/productStore';
  import { authStore } from '$lib/stores/auth';
  import AuditLogTable from '../../features/audit/components/AuditLogTable.svelte';
  import ApprovalPanel from '../../features/audit/components/ApprovalPanel.svelte';
  import SnapshotPanel from '../../features/audit/components/SnapshotPanel.svelte';
  import EvidencePanel from '../../features/audit/components/EvidencePanel.svelte';

  type TabId = 'logs' | 'approvals' | 'snapshots' | 'evidence';

  const TABS: { id: TabId; label: string; description: string }[] = [
    { id: 'logs', label: 'Audit Log', description: 'Change history on all artifacts' },
    { id: 'approvals', label: 'Approvals', description: 'Workflow state & sign-offs' },
    { id: 'snapshots', label: 'TARA Snapshots', description: 'Versioned point-in-time captures' },
    { id: 'evidence', label: 'Evidence', description: 'Attached files & documents' },
  ];

  let activeTab: TabId = 'logs';

  $: scopeId = $selectedProduct?.scope_id || '';
</script>

<div class="p-6 max-w-7xl mx-auto">
  <!-- Header -->
  <div class="mb-6">
    <h1 class="text-sm font-bold" style="color: var(--color-text-primary);">Audit & Compliance</h1>
    {#if $selectedProduct}
      <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">
        Product: <span class="font-medium" style="color: var(--color-text-secondary);">{$selectedProduct.name}</span>
      </p>
    {:else}
      <p class="text-xs mt-1" style="color: var(--color-error);">Select a product from the sidebar to view audit data.</p>
    {/if}
  </div>

  {#if !scopeId}
    <div class="rounded-lg p-6 text-center" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
      <p class="text-xs font-medium" style="color: var(--color-text-primary);">No product selected</p>
      <p class="text-[11px] mt-1" style="color: var(--color-text-tertiary);">Go to Product Scope and select a product first.</p>
    </div>
  {:else}
    <!-- Tabs -->
    <div class="mb-6" style="border-bottom: 1px solid var(--color-border-default);">
      <nav class="flex gap-6">
        {#each TABS as tab}
          <button
            on:click={() => activeTab = tab.id}
            class="pb-3 text-xs font-medium border-b-2 transition-colors"
            style="{activeTab === tab.id
                ? 'border-color: var(--color-accent-primary); color: var(--color-accent-primary);'
                : 'border-color: transparent; color: var(--color-text-tertiary);'}"
          >
            {tab.label}
          </button>
        {/each}
      </nav>
    </div>

    <!-- Tab description -->
    <p class="text-xs mb-4" style="color: var(--color-text-tertiary);">
      {TABS.find(t => t.id === activeTab)?.description}
    </p>

    <!-- Tab content -->
    {#if activeTab === 'logs'}
      <AuditLogTable {scopeId} />
    {:else if activeTab === 'approvals'}
      <ApprovalPanel {scopeId} />
    {:else if activeTab === 'snapshots'}
      <SnapshotPanel {scopeId} />
    {:else if activeTab === 'evidence'}
      <EvidencePanel {scopeId} />
    {/if}
  {/if}
</div>
