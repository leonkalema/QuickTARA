<script lang="ts">
  import type { CraRequirementStatusRecord, UpdateRequirementRequest } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { ChevronDown, ChevronRight, Check, Circle, AlertTriangle, Minus } from '@lucide/svelte';

  interface Props {
    requirements: CraRequirementStatusRecord[];
    onupdate?: () => void;
  }

  let { requirements, onupdate }: Props = $props();

  let expandedId: string | null = $state(null);
  let editingId: string | null = $state(null);
  let editForm: UpdateRequirementRequest = $state({});
  let saving = $state(false);

  const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
    not_started: { label: 'Not Started', color: 'var(--color-text-tertiary)' },
    partial: { label: 'Partial', color: 'var(--color-status-warning)' },
    compliant: { label: 'Compliant', color: 'var(--color-status-success)' },
    not_applicable: { label: 'N/A', color: 'var(--color-text-tertiary)' },
  } as const;


  const CATEGORY_LABELS: Record<string, string> = {
    technical: 'Technical',
    process: 'Process',
    documentation: 'Documentation',
  } as const;

  function toggleExpand(id: string): void {
    expandedId = expandedId === id ? null : id;
    editingId = null;
  }

  function startEdit(req: CraRequirementStatusRecord): void {
    editingId = req.id;
    editForm = {
      status: req.status,
      owner: req.owner ?? '',
      target_date: req.target_date ?? '',
      evidence_notes: req.evidence_notes ?? '',
    };
  }


  function cancelEdit(): void {
    editingId = null;
    editForm = {};
  }

  async function saveEdit(id: string): Promise<void> {
    saving = true;
    try {
      await craApi.updateRequirement(id, editForm);
      editingId = null;
      onupdate?.();
    } catch (err) {
      console.error('Failed to update requirement:', err);
    } finally {
      saving = false;
    }
  }
</script>

<div class="rounded-lg border overflow-hidden" style="border-color: var(--color-border-default);">
  <!-- Header -->
  <div
    class="grid grid-cols-[2rem_1fr_6rem_8rem_6rem_4rem] gap-2 px-4 py-2 text-xs font-semibold uppercase tracking-wider"
    style="background: var(--color-bg-surface-hover); color: var(--color-text-tertiary);"
  >
    <div></div>
    <div>Requirement</div>
    <div>Article</div>
    <div>Status</div>
    <div>Owner</div>
    <div>Auto</div>
  </div>

  <!-- Rows -->
  {#each requirements as req (req.id)}
    {@const config = STATUS_CONFIG[req.status] ?? STATUS_CONFIG.not_started}
    {@const expanded = expandedId === req.id}
    {@const editing = editingId === req.id}

    <div class="border-t" style="border-color: var(--color-border-subtle);">
      <!-- Summary row -->
      <button
        class="w-full grid grid-cols-[2rem_1fr_6rem_8rem_6rem_4rem] gap-2 px-4 py-3 text-sm items-center transition-colors cursor-pointer"
        style="background: {expanded ? 'var(--color-bg-surface-hover)' : 'var(--color-bg-surface)'}; color: var(--color-text-primary);"
        onclick={() => toggleExpand(req.id)}
      >
        <div style="color: var(--color-text-tertiary);">
          {#if expanded}
            <ChevronDown class="w-4 h-4" />
          {:else}
            <ChevronRight class="w-4 h-4" />
          {/if}
        </div>
        <div class="text-left">
          <span class="font-medium">{req.requirement_id}</span>
          <span class="ml-2" style="color: var(--color-text-secondary);">{req.requirement_name ?? ''}</span>
        </div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">{req.requirement_article ?? ''}</div>
        <div>
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
            style="color: {config.color}; background: {config.color}15;"
          >
            {#if req.status === 'compliant'}
              <Check class="w-3 h-3" />
            {:else if req.status === 'partial'}
              <AlertTriangle class="w-3 h-3" />
            {:else if req.status === 'not_applicable'}
              <Minus class="w-3 h-3" />
            {:else}
              <Circle class="w-3 h-3" />
            {/if}
            {config.label}
          </span>
        </div>
        <div class="text-xs truncate" style="color: var(--color-text-secondary);">{req.owner ?? '—'}</div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">
          {#if req.auto_mapped}
            <span class="px-1.5 py-0.5 rounded text-xs" style="background: var(--color-accent-primary)20; color: var(--color-accent-primary);">Auto</span>
          {/if}
        </div>
      </button>

      <!-- Expanded detail -->
      {#if expanded}
        <div class="px-4 pb-4 pt-2 space-y-3" style="background: var(--color-bg-surface-hover);">
          {#if !editing}
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Evidence</div>
                <div style="color: var(--color-text-secondary);">{req.evidence_notes || '—'}</div>
              </div>
              <div>
                <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Owner</div>
                <div style="color: var(--color-text-secondary);">{req.owner || '—'}</div>
              </div>
              <div>
                <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Target Date</div>
                <div style="color: var(--color-text-secondary);">{req.target_date || '—'}</div>
              </div>
              {#if req.auto_mapped && req.mapped_artifact_type}
                <div>
                  <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">TARA Evidence</div>
                  <div style="color: var(--color-accent-primary);">
                    {req.mapped_artifact_count} {req.mapped_artifact_type}(s)
                  </div>
                </div>
              {/if}
            </div>
            <button
              class="px-3 py-1.5 rounded text-xs font-medium transition-colors cursor-pointer"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              onclick={() => startEdit(req)}
            >
              Edit
            </button>
          {:else}
            <!-- Edit form -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label for="req-status" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Status</label>
                <select
                  id="req-status"
                  class="w-full px-2 py-1.5 rounded text-sm border"
                  style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
                  bind:value={editForm.status}
                >
                  <option value="not_started">Not Started</option>
                  <option value="partial">Partial</option>
                  <option value="compliant">Compliant</option>
                  <option value="not_applicable">N/A</option>
                </select>
              </div>
              <div>
                <label for="req-owner" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Owner</label>
                <input
                  id="req-owner"
                  type="text"
                  class="w-full px-2 py-1.5 rounded text-sm border"
                  style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
                  bind:value={editForm.owner}
                  placeholder="Responsible person"
                />
              </div>
              <div>
                <label for="req-target-date" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Target Date</label>
                <input
                  id="req-target-date"
                  type="date"
                  class="w-full px-2 py-1.5 rounded text-sm border"
                  style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
                  bind:value={editForm.target_date}
                />
              </div>
              <div class="col-span-2">
                <label for="req-evidence" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Evidence Notes</label>
                <textarea
                  id="req-evidence"
                  class="w-full px-2 py-1.5 rounded text-sm border resize-none"
                  style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
                  rows="2"
                  bind:value={editForm.evidence_notes}
                  placeholder="What evidence exists for this requirement?"
                ></textarea>
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button
                class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
                style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
                onclick={() => saveEdit(req.id)}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
                style="background: var(--color-bg-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
                onclick={cancelEdit}
              >
                Cancel
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/each}
</div>
