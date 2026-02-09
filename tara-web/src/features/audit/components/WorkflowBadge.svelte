<script lang="ts">
  import { auditApi } from '$lib/api/auditApi';
  import type { ApprovalWorkflow } from '$lib/api/auditApi';
  import { authStore } from '$lib/stores/auth';
  import { notifications } from '$lib/stores/notificationStore';
  import { canCreateWorkflow, filterAllowedTransitions } from '$lib/utils/workflow-permissions';

  export let artifactType: string;
  export let artifactId: string;
  export let scopeId: string;

  let workflow: ApprovalWorkflow | null = null;
  let loading = false;
  let showActions = false;
  let transitionNotes = '';

  const STATE_STYLES: Record<string, string> = {
    draft: 'background: var(--color-bg-elevated); color: var(--color-text-secondary);',
    review: 'background: color-mix(in srgb, var(--color-status-draft-text, #f59e0b) 15%, transparent); color: var(--color-status-draft-text, #f59e0b);',
    approved: 'background: color-mix(in srgb, var(--color-status-accepted-text, #10b981) 15%, transparent); color: var(--color-status-accepted-text, #10b981);',
    released: 'background: color-mix(in srgb, var(--color-accent-primary) 15%, transparent); color: var(--color-accent-primary);',
  };

  const STATE_LABELS: Record<string, string> = {
    draft: 'Draft',
    review: 'In Review',
    approved: 'Approved',
    released: 'Released',
  };

  const TRANSITION_STYLES: Record<string, string> = {
    review: 'background: var(--color-status-draft-text, #f59e0b); color: var(--color-text-inverse);',
    draft: 'background: var(--color-bg-elevated); color: var(--color-text-secondary);',
    approved: 'background: var(--color-status-accepted-text, #10b981); color: var(--color-text-inverse);',
    released: 'background: var(--color-accent-primary); color: var(--color-text-inverse);',
  };

  const TRANSITIONS: Record<string, { target: string; label: string }[]> = {
    draft: [{ target: 'review', label: 'Submit for Review' }],
    review: [
      { target: 'draft', label: 'Return to Draft' },
      { target: 'approved', label: 'Approve' },
    ],
    approved: [
      { target: 'review', label: 'Reopen Review' },
      { target: 'released', label: 'Release' },
    ],
    released: [],
  };

  async function loadWorkflow(): Promise<void> {
    try {
      workflow = await auditApi.getWorkflow(artifactType, artifactId);
    } catch {
      workflow = null;
    }
  }

  async function startWorkflow(): Promise<void> {
    loading = true;
    try {
      workflow = await auditApi.createWorkflow(artifactType, artifactId, scopeId);
      notifications.show('Approval workflow started', 'success');
    } catch (e: any) {
      notifications.show(e.message || 'Failed to create workflow', 'error');
    } finally {
      loading = false;
    }
  }

  async function doTransition(target: string): Promise<void> {
    loading = true;
    try {
      workflow = await auditApi.transitionWorkflow(
        artifactType, artifactId, target, transitionNotes || undefined,
      );
      showActions = false;
      transitionNotes = '';
      notifications.show(`Workflow moved to ${STATE_LABELS[target]}`, 'success');
    } catch (e: any) {
      notifications.show(e.message || 'Transition failed', 'error');
    } finally {
      loading = false;
    }
  }

  $: if (artifactId) loadWorkflow();
  $: allowedActions = workflow
    ? filterAllowedTransitions(TRANSITIONS[workflow.current_state] || [], workflow.created_by)
    : [];
  $: showCreate = canCreateWorkflow();
</script>

<div class="inline-flex items-center gap-2">
  {#if workflow}
    <button
      on:click={() => showActions = !showActions}
      class="px-2 py-0.5 rounded-full text-[10px] font-medium cursor-pointer"
      style="{STATE_STYLES[workflow.current_state] || 'background: var(--color-bg-elevated); color: var(--color-text-tertiary);'}"
      title="Click to manage workflow"
    >
      {STATE_LABELS[workflow.current_state] || workflow.current_state}
    </button>

    {#if showActions && allowedActions.length > 0}
      <div class="flex items-center gap-1">
        {#each allowedActions as action}
          <button
            on:click={() => doTransition(action.target)}
            disabled={loading}
            class="px-2 py-0.5 rounded text-[10px] font-medium disabled:opacity-50"
            style="{TRANSITION_STYLES[action.target] || ''}"
          >
            {action.label}
          </button>
        {/each}
      </div>
    {:else if showActions}
      <span class="text-[10px] italic" style="color: var(--color-text-tertiary);">No actions available for your role</span>
    {/if}
  {:else if showCreate}
    <button
      on:click={startWorkflow}
      disabled={loading}
      class="px-2 py-0.5 rounded text-[10px] font-medium disabled:opacity-50"
      style="background: var(--color-bg-elevated); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
      title="Start approval workflow"
    >
      {loading ? '...' : 'Start Workflow'}
    </button>
  {/if}
</div>
