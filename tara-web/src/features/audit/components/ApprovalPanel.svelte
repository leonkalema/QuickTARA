<script lang="ts">
  import { auditApi } from '$lib/api/auditApi';
  import type { ApprovalWorkflow, Signoff } from '$lib/api/auditApi';
  import { authStore } from '$lib/stores/auth';
  import { filterAllowedTransitions } from '$lib/utils/workflow-permissions';

  export let scopeId: string;

  let workflows: ApprovalWorkflow[] = [];
  let loading = false;
  let stateFilter = '';
  let selectedWf: ApprovalWorkflow | null = null;
  let signoffs: Signoff[] = [];
  let showTransition = false;
  let transitionTarget = '';
  let transitionNotes = '';

  const STATE_COLORS: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    review: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    released: 'bg-blue-100 text-blue-800',
  };

  const TRANSITIONS: Record<string, { target: string; label: string; color: string }[]> = {
    draft: [{ target: 'review', label: 'Submit for Review', color: 'bg-yellow-500 text-white' }],
    review: [
      { target: 'draft', label: 'Return to Draft', color: 'bg-gray-500 text-white' },
      { target: 'approved', label: 'Approve', color: 'bg-green-600 text-white' },
    ],
    approved: [
      { target: 'review', label: 'Reopen Review', color: 'bg-yellow-500 text-white' },
      { target: 'released', label: 'Release', color: 'bg-blue-600 text-white' },
    ],
    released: [],
  };

  async function loadWorkflows(): Promise<void> {
    loading = true;
    try {
      workflows = await auditApi.listWorkflowsByScope(scopeId, stateFilter || undefined);
    } catch (e) {
      console.error('Failed to load workflows', e);
    } finally {
      loading = false;
    }
  }

  async function selectWorkflow(wf: ApprovalWorkflow): Promise<void> {
    selectedWf = wf;
    showTransition = false;
    try {
      signoffs = await auditApi.getSignoffs(wf.id);
    } catch { signoffs = []; }
  }

  async function doTransition(): Promise<void> {
    if (!selectedWf || !transitionTarget) return;
    try {
      const updated = await auditApi.transitionWorkflow(
        selectedWf.artifact_type, selectedWf.artifact_id,
        transitionTarget, transitionNotes || undefined,
      );
      selectedWf = updated;
      showTransition = false;
      transitionTarget = '';
      transitionNotes = '';
      loadWorkflows();
    } catch (e: any) {
      alert(e.message || 'Transition failed');
    }
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  $: if (scopeId) loadWorkflows();
  $: allowedTransitions = selectedWf
    ? filterAllowedTransitions(
        TRANSITIONS[selectedWf.current_state] || [],
        selectedWf.created_by,
      )
    : [];
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <!-- Workflow list -->
  <div>
    <div class="flex items-center gap-3 mb-4">
      <select bind:value={stateFilter} on:change={() => loadWorkflows()}
        class="rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
        <option value="">All states</option>
        <option value="draft">Draft</option>
        <option value="review">In Review</option>
        <option value="approved">Approved</option>
        <option value="released">Released</option>
      </select>
      <span class="text-xs" style="color: var(--color-text-tertiary);">{workflows.length} workflows</span>
    </div>

    {#if loading}
      <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">Loading...</div>
    {:else if workflows.length === 0}
      <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">No approval workflows yet.
        <p class="text-[11px] mt-1" style="color: var(--color-text-tertiary);">Workflows are created when artifacts are submitted for review.</p>
      </div>
    {:else}
      <div class="space-y-2">
        {#each workflows as wf}
          <button on:click={() => selectWorkflow(wf)}
            class="w-full text-left p-3 rounded-lg transition-colors"
            style="{selectedWf?.id === wf.id ? 'border: 1px solid var(--color-accent-primary); background: var(--color-bg-elevated);' : 'border: 1px solid var(--color-border-default);'}">
            <div class="flex items-center justify-between">
              <div>
                <span class="font-mono text-[10px]" style="color: var(--color-text-tertiary);">{wf.artifact_type}</span>
                <p class="text-xs font-medium" style="color: var(--color-text-primary);">{wf.artifact_id}</p>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium {STATE_COLORS[wf.current_state] || 'bg-gray-100'}">
                {wf.current_state}
              </span>
            </div>
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">by {wf.created_by} · {formatDate(wf.updated_at)}</p>
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Workflow detail -->
  <div>
    {#if selectedWf}
      <div class="rounded-lg p-4" style="border: 1px solid var(--color-border-default);">
        <h3 class="font-semibold text-xs mb-3" style="color: var(--color-text-primary);">
          {selectedWf.artifact_id}
          <span class="ml-2 px-2 py-0.5 rounded-full text-xs font-medium {STATE_COLORS[selectedWf.current_state]}">
            {selectedWf.current_state}
          </span>
        </h3>
        <dl class="grid grid-cols-2 gap-2 text-xs mb-4">
          <dt style="color: var(--color-text-tertiary);">Created by</dt><dd style="color: var(--color-text-secondary);">{selectedWf.created_by}</dd>
          {#if selectedWf.approved_by}
            <dt style="color: var(--color-text-tertiary);">Approved by</dt><dd style="color: var(--color-text-secondary);">{selectedWf.approved_by}</dd>
          {/if}
          {#if selectedWf.released_by}
            <dt style="color: var(--color-text-tertiary);">Released by</dt><dd style="color: var(--color-text-secondary);">{selectedWf.released_by}</dd>
          {/if}
          {#if selectedWf.review_notes}
            <dt style="color: var(--color-text-tertiary);">Review notes</dt><dd style="color: var(--color-text-secondary);">{selectedWf.review_notes}</dd>
          {/if}
          {#if selectedWf.approval_notes}
            <dt style="color: var(--color-text-tertiary);">Approval notes</dt><dd style="color: var(--color-text-secondary);">{selectedWf.approval_notes}</dd>
          {/if}
        </dl>

        <!-- Transition buttons (role-gated) -->
        {#if allowedTransitions.length > 0}
          <div class="flex gap-2 mb-4">
            {#each allowedTransitions as action}
              <button on:click={() => { transitionTarget = action.target; showTransition = true; }}
                class="px-3 py-1.5 text-xs rounded-md {action.color}">
                → {action.label}
              </button>
            {/each}
          </div>
        {:else if (TRANSITIONS[selectedWf.current_state]?.length ?? 0) > 0}
          <p class="text-[10px] italic mb-4" style="color: var(--color-text-tertiary);">No transitions available for your role</p>
        {/if}

        {#if showTransition}
          <div class="rounded-md p-3 mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
            <p class="text-xs font-medium mb-2" style="color: var(--color-text-primary);">Transition to: <strong>{transitionTarget}</strong></p>
            <textarea bind:value={transitionNotes} placeholder="Notes (optional)"
              class="w-full rounded-md p-2 text-xs mb-2" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" rows="2"></textarea>
            <div class="flex gap-2">
              <button on:click={doTransition}
                class="px-3 py-1 text-xs rounded-md" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Confirm</button>
              <button on:click={() => showTransition = false}
                class="px-3 py-1 text-xs rounded-md" style="border: 1px solid var(--color-border-default); color: var(--color-text-secondary);">Cancel</button>
            </div>
          </div>
        {/if}

        <!-- Sign-off history -->
        <h4 class="text-xs font-medium mb-2" style="color: var(--color-text-secondary);">Sign-offs</h4>
        {#if signoffs.length === 0}
          <p class="text-[10px]" style="color: var(--color-text-tertiary);">No sign-offs yet</p>
        {:else}
          <div class="space-y-2">
            {#each signoffs as so}
              <div class="text-xs p-2 rounded" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
                <span class="font-medium">{so.signer}</span>
                <span style="color: var(--color-text-tertiary);">({so.signer_role})</span> —
                <span class="{so.action === 'approve' ? 'text-green-600' : 'text-red-600'} font-medium">{so.action}</span>
                {#if so.comment}<p class="mt-1" style="color: var(--color-text-secondary);">{so.comment}</p>{/if}
                <p class="mt-1" style="color: var(--color-text-tertiary);">{formatDate(so.signed_at)}</p>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {:else}
      <div class="text-center py-12 text-xs" style="color: var(--color-text-tertiary);">Select a workflow to view details</div>
    {/if}
  </div>
</div>
