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
    <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">Audit & Compliance</h1>
    <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
      {#if $selectedProduct}
        Change history, approvals, and evidence for <strong style="color: var(--color-text-primary);">{$selectedProduct.name}</strong>.
      {:else}
        Select a product to view its audit trail and compliance records.
      {/if}
    </p>
  </div>

  {#if !scopeId}
    <div class="rounded-xl border border-dashed py-20 text-center" style="border-color: var(--color-border-default);">
      <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style="background: var(--color-bg-elevated);">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
      </div>
      <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No product selected</h3>
      <p class="text-sm mb-6 max-w-sm mx-auto" style="color: var(--color-text-tertiary);">Select a product from the header dropdown to view its audit trail, approvals, and evidence.</p>
      <a href="/products" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Go to Products</a>
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
