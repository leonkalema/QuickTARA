<script lang="ts">
  import { auditApi } from '$lib/api/auditApi';
  import type { TaraSnapshot, TaraSnapshotDetail } from '$lib/api/auditApi';
  import { authStore } from '$lib/stores/auth';

  export let scopeId: string;

  let snapshots: TaraSnapshot[] = [];
  let loading = false;
  let creating = false;
  let versionLabel = '';
  let notes = '';
  let showCreate = false;
  let selectedDetail: TaraSnapshotDetail | null = null;
  let loadingDetail = false;

  async function loadSnapshots(): Promise<void> {
    loading = true;
    try {
      snapshots = await auditApi.listSnapshots(scopeId);
    } catch (e) {
      console.error('Failed to load snapshots', e);
    } finally {
      loading = false;
    }
  }

  async function createSnapshot(): Promise<void> {
    creating = true;
    const user = $authStore.user?.email || 'unknown';
    try {
      await auditApi.createSnapshot(scopeId, user, versionLabel || undefined, notes || undefined);
      showCreate = false;
      versionLabel = '';
      notes = '';
      loadSnapshots();
    } catch (e) {
      console.error('Failed to create snapshot', e);
    } finally {
      creating = false;
    }
  }

  async function viewDetail(snap: TaraSnapshot): Promise<void> {
    loadingDetail = true;
    try {
      selectedDetail = await auditApi.getSnapshotDetail(snap.snapshot_id);
    } catch (e) {
      console.error('Failed to load snapshot detail', e);
    } finally {
      loadingDetail = false;
    }
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  $: if (scopeId) loadSnapshots();
</script>

<div>
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-xs font-medium" style="color: var(--color-text-secondary);">{snapshots.length} snapshots</h3>
    <button on:click={() => showCreate = !showCreate}
      class="px-3 py-1.5 text-xs rounded-md" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
      Create Snapshot
    </button>
  </div>

  {#if showCreate}
    <div class="rounded-lg p-4 mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label for="snap-label" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Version Label</label>
          <input id="snap-label" bind:value={versionLabel} placeholder="e.g. v1.0, RC-1"
            class="w-full rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
        </div>
        <div>
          <label for="snap-notes" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Notes</label>
          <input id="snap-notes" bind:value={notes} placeholder="Reason for snapshot"
            class="w-full rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
        </div>
      </div>
      <div class="flex gap-2">
        <button on:click={createSnapshot} disabled={creating}
          class="px-3 py-1.5 text-xs rounded-md disabled:opacity-50" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
          {creating ? 'Creating...' : 'Capture Snapshot'}
        </button>
        <button on:click={() => showCreate = false}
          class="px-3 py-1.5 text-xs rounded-md" style="border: 1px solid var(--color-border-default); color: var(--color-text-secondary);">Cancel</button>
      </div>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">Loading snapshots...</div>
  {:else if snapshots.length === 0}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">
      No TARA snapshots yet. Create one to capture the current state.
    </div>
  {:else}
    <div class="space-y-3">
      {#each snapshots as snap}
        <div class="rounded-lg p-4 transition-colors" style="border: 1px solid var(--color-border-default);">
          <div class="flex items-center justify-between mb-2">
            <div>
              <span class="text-xs font-semibold" style="color: var(--color-text-primary);">{snap.version_label || `v${snap.version}`}</span>
              <span class="text-[10px] ml-2" style="color: var(--color-text-tertiary);">by {snap.created_by}</span>
            </div>
            <span class="text-[10px]" style="color: var(--color-text-tertiary);">{formatDate(snap.created_at)}</span>
          </div>
          <div class="grid grid-cols-5 gap-2 text-center mb-3">
            <div class="rounded p-2" style="background: var(--color-bg-elevated);">
              <p class="text-sm font-bold" style="color: var(--color-text-primary);">{snap.asset_count}</p>
              <p class="text-[10px]" style="color: var(--color-text-tertiary);">Assets</p>
            </div>
            <div class="rounded p-2" style="background: var(--color-bg-elevated);">
              <p class="text-sm font-bold" style="color: var(--color-text-primary);">{snap.damage_scenario_count}</p>
              <p class="text-[10px]" style="color: var(--color-text-tertiary);">DS</p>
            </div>
            <div class="rounded p-2" style="background: var(--color-bg-elevated);">
              <p class="text-sm font-bold" style="color: var(--color-text-primary);">{snap.threat_scenario_count}</p>
              <p class="text-[10px]" style="color: var(--color-text-tertiary);">TS</p>
            </div>
            <div class="rounded p-2" style="background: var(--color-bg-elevated);">
              <p class="text-sm font-bold" style="color: var(--color-text-primary);">{snap.attack_path_count}</p>
              <p class="text-[10px]" style="color: var(--color-text-tertiary);">AP</p>
            </div>
            <div class="rounded p-2" style="background: var(--color-bg-elevated);">
              <p class="text-sm font-bold" style="color: var(--color-text-primary);">{snap.risk_treatment_count}</p>
              <p class="text-[10px]" style="color: var(--color-text-tertiary);">RT</p>
            </div>
          </div>
          {#if snap.notes}
            <p class="text-[10px] mb-2" style="color: var(--color-text-tertiary);">{snap.notes}</p>
          {/if}
          <button on:click={() => viewDetail(snap)}
            class="text-[10px] hover:underline" style="color: var(--color-accent-primary);">View full snapshot data</button>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Detail modal -->
  {#if selectedDetail}
    <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
      role="dialog" aria-modal="true" tabindex="-1"
      on:click|self={() => selectedDetail = null}
      on:keydown={(e) => { if (e.key === 'Escape') selectedDetail = null; }}>
      <div class="rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-xs" style="color: var(--color-text-primary);">
            Snapshot: {selectedDetail.version_label || `v${selectedDetail.version}`}
          </h3>
          <button on:click={() => selectedDetail = null} class="text-xl" style="color: var(--color-text-tertiary);">&times;</button>
        </div>
        <pre class="rounded p-4 text-xs overflow-x-auto max-h-[60vh]" style="background: var(--color-bg-inset); color: var(--color-text-secondary);">{JSON.stringify(selectedDetail.snapshot_data, null, 2)}</pre>
      </div>
    </div>
  {/if}
</div>
