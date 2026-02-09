<script lang="ts">
  import { onMount } from 'svelte';
  import { auditApi } from '$lib/api/auditApi';
  import type { AuditLogEntry } from '$lib/api/auditApi';

  export let scopeId: string;

  let logs: AuditLogEntry[] = [];
  let total = 0;
  let loading = false;
  let filterType = '';
  let page = 0;
  const PAGE_SIZE = 20;

  async function loadLogs(): Promise<void> {
    loading = true;
    try {
      const res = await auditApi.getLogs({
        scope_id: scopeId,
        artifact_type: filterType || undefined,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      });
      logs = res.logs;
      total = res.total;
    } catch (e) {
      console.error('Failed to load audit logs', e);
    } finally {
      loading = false;
    }
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  function actionBadgeClass(action: string): string {
    const map: Record<string, string> = {
      create: 'bg-green-100 text-green-800',
      update: 'bg-blue-100 text-blue-800',
      delete: 'bg-red-100 text-red-800',
      status_change: 'bg-yellow-100 text-yellow-800',
      workflow_created: 'bg-purple-100 text-purple-800',
      evidence_attached: 'bg-indigo-100 text-indigo-800',
      evidence_removed: 'bg-red-100 text-red-800',
    };
    return map[action] || 'bg-gray-100 text-gray-800';
  }

  function prevPage(): void {
    if (page > 0) { page--; loadLogs(); }
  }
  function nextPage(): void {
    if ((page + 1) * PAGE_SIZE < total) { page++; loadLogs(); }
  }

  $: if (scopeId) { page = 0; loadLogs(); }
</script>

<div>
  <!-- Filter bar -->
  <div class="flex items-center gap-3 mb-4">
    <select bind:value={filterType} on:change={() => { page = 0; loadLogs(); }}
      class="rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
      <option value="">All types</option>
      <option value="damage_scenario">Damage Scenarios</option>
      <option value="threat_scenario">Threat Scenarios</option>
      <option value="asset">Assets</option>
      <option value="tara_snapshot">Snapshots</option>
    </select>
    <span class="text-xs" style="color: var(--color-text-tertiary);">{total} entries</span>
  </div>

  {#if loading}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">Loading audit log...</div>
  {:else if logs.length === 0}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">No audit entries yet</div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full text-xs">
        <thead style="background: var(--color-bg-elevated);">
          <tr>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">When</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Who</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Action</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Artifact</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Details</th>
          </tr>
        </thead>
        <tbody>
          {#each logs as log}
            <tr style="border-bottom: 1px solid var(--color-border-subtle);">
              <td class="px-4 py-2 whitespace-nowrap" style="color: var(--color-text-tertiary);">{formatDate(log.performed_at)}</td>
              <td class="px-4 py-2" style="color: var(--color-text-secondary);">{log.performed_by}</td>
              <td class="px-4 py-2">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium {actionBadgeClass(log.action)}">
                  {log.action}
                </span>
              </td>
              <td class="px-4 py-2">
                <span class="text-[10px]" style="color: var(--color-text-tertiary);">{log.artifact_type}</span><br/>
                <span class="font-mono text-[10px]" style="color: var(--color-text-secondary);">{log.artifact_id}</span>
              </td>
              <td class="px-4 py-2" style="color: var(--color-text-secondary);">
                {#if log.change_summary}
                  {log.change_summary}
                {:else if log.field_changed}
                  <span class="font-medium">{log.field_changed}</span>:
                  <span class="line-through text-red-500">{log.old_value}</span> →
                  <span class="text-green-600">{log.new_value}</span>
                {:else}
                  —
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between mt-4 text-xs" style="color: var(--color-text-tertiary);">
      <span>Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}</span>
      <div class="flex gap-2">
        <button on:click={prevPage} disabled={page === 0}
          class="px-3 py-1 rounded text-xs disabled:opacity-40" style="border: 1px solid var(--color-border-default); color: var(--color-text-secondary);">Prev</button>
        <button on:click={nextPage} disabled={(page + 1) * PAGE_SIZE >= total}
          class="px-3 py-1 rounded text-xs disabled:opacity-40" style="border: 1px solid var(--color-border-default); color: var(--color-text-secondary);">Next</button>
      </div>
    </div>
  {/if}
</div>
