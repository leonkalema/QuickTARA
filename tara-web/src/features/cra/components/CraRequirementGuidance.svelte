<script lang="ts">
  import type { RequirementGuidance } from '$lib/types/cra';
  import {
    BookOpen, CheckSquare, HelpCircle, AlertTriangle, Link,
    Wrench, ClipboardList, Clock, Shield
  } from '@lucide/svelte';

  interface Props {
    guidance: RequirementGuidance;
  }

  let { guidance }: Props = $props();

  type TabId = 'overview' | 'sub_reqs' | 'evidence' | 'remediation' | 'investigate' | 'gaps';
  let activeTab: TabId = $state('overview');

  const TABS: Array<{ id: TabId; label: string; icon: any }> = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'sub_reqs', label: 'Sub-Requirements', icon: ClipboardList },
    { id: 'evidence', label: 'Evidence', icon: CheckSquare },
    { id: 'remediation', label: 'Remediation', icon: Wrench },
    { id: 'investigate', label: 'Ask Team', icon: HelpCircle },
    { id: 'gaps', label: 'Gaps', icon: AlertTriangle },
  ];

  const PRIORITY_COLORS: Record<string, string> = {
    Critical: 'var(--color-status-error)',
    High: '#f59e0b',
    Medium: 'var(--color-accent-primary)',
    Low: 'var(--color-status-success)',
  } as const;

  let totalEffortDays = $derived(
    guidance.remediation_actions.reduce((sum, a) => sum + a.effort_days, 0)
  );
</script>

<div class="rounded-lg border mt-3" style="border-color: var(--color-accent-primary)30; background: var(--color-accent-primary)05;">
  <!-- Header bar with priority, article, deadline -->
  <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color: var(--color-accent-primary)20;">
    <div class="flex items-center gap-2">
      <Shield class="w-3.5 h-3.5" style="color: var(--color-accent-primary);" />
      <span class="text-xs font-semibold" style="color: var(--color-accent-primary);">
        {guidance.cra_article}
      </span>
    </div>
    <div class="flex items-center gap-2">
      <span
        class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase"
        style="background: {PRIORITY_COLORS[guidance.priority] ?? 'var(--color-text-tertiary)'}15; color: {PRIORITY_COLORS[guidance.priority] ?? 'var(--color-text-tertiary)'};"
      >
        {guidance.priority}
      </span>
      <span class="flex items-center gap-1 text-[10px]" style="color: var(--color-text-tertiary);">
        <Clock class="w-3 h-3" />
        {guidance.deadline_note}
      </span>
    </div>
  </div>

  <!-- Tab bar -->
  <div class="flex gap-0.5 px-3 pt-2 flex-wrap">
    {#each TABS as tab (tab.id)}
      <button
        class="flex items-center gap-1 px-2 py-1.5 rounded text-[11px] font-medium transition-colors cursor-pointer"
        style="
          background: {activeTab === tab.id ? 'var(--color-accent-primary)15' : 'transparent'};
          color: {activeTab === tab.id ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'};
        "
        onclick={() => activeTab = tab.id}
      >
        <tab.icon class="w-3 h-3" />
        {tab.label}
      </button>
    {/each}
  </div>

  <!-- Tab content -->
  <div class="px-4 py-3">
    {#if activeTab === 'overview'}
      <p class="text-sm leading-relaxed mb-3" style="color: var(--color-text-secondary);">
        {guidance.explanation}
      </p>
      <div class="rounded border px-3 py-2 mb-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <p class="text-[10px] font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-tertiary);">
          Regulatory Text
        </p>
        <p class="text-xs italic leading-relaxed" style="color: var(--color-text-secondary);">
          "{guidance.regulatory_text}"
        </p>
      </div>
      <div class="grid grid-cols-2 gap-2 text-xs">
        {#if guidance.mapped_controls.length > 0}
          <div>
            <span class="font-semibold" style="color: var(--color-text-tertiary);">Mapped Controls:</span>
            <span style="color: var(--color-text-secondary);"> {guidance.mapped_controls.join(', ')}</span>
          </div>
        {/if}
        {#if guidance.mapped_standards.length > 0}
          <div>
            <span class="font-semibold" style="color: var(--color-text-tertiary);">Standards:</span>
            <span style="color: var(--color-text-secondary);"> {guidance.mapped_standards.join(', ')}</span>
          </div>
        {/if}
      </div>
      <div class="flex items-start gap-2 mt-3 pt-3 border-t" style="border-color: var(--color-border-subtle);">
        <Link class="w-3 h-3 mt-0.5 shrink-0" style="color: var(--color-accent-primary);" />
        <p class="text-xs" style="color: var(--color-text-tertiary);">
          <span class="font-medium" style="color: var(--color-text-secondary);">TARA link:</span>
          {guidance.tara_link}
        </p>
      </div>

    {:else if activeTab === 'sub_reqs'}
      <p class="text-xs mb-2 font-medium" style="color: var(--color-text-tertiary);">
        Check each sub-requirement individually:
      </p>
      <div class="space-y-2">
        {#each guidance.sub_requirements as sub, i}
          <div class="rounded border px-3 py-2" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
            <div class="flex items-start gap-2">
              <span class="text-[10px] font-bold rounded px-1 py-0.5 shrink-0 mt-0.5" style="background: var(--color-accent-primary)15; color: var(--color-accent-primary);">
                {i + 1}
              </span>
              <div class="flex-1">
                <p class="text-xs font-semibold" style="color: var(--color-text-primary);">{sub.description}</p>
                <p class="text-[11px] mt-1" style="color: var(--color-status-success);">
                  <span class="font-medium">Evidence:</span> {sub.check_evidence}
                </p>
                <p class="text-[11px] mt-0.5" style="color: var(--color-status-warning);">
                  <span class="font-medium">Typical gap:</span> {sub.typical_gap}
                </p>
              </div>
            </div>
          </div>
        {/each}
      </div>

    {:else if activeTab === 'evidence'}
      <p class="text-xs mb-2 font-medium" style="color: var(--color-text-tertiary);">
        Collect these artifacts to satisfy this requirement:
      </p>
      <ul class="space-y-1.5">
        {#each guidance.evidence_checklist as item}
          <li class="flex items-start gap-2 text-xs" style="color: var(--color-text-secondary);">
            <CheckSquare class="w-3.5 h-3.5 mt-0.5 shrink-0" style="color: var(--color-status-success);" />
            {item}
          </li>
        {/each}
      </ul>

    {:else if activeTab === 'remediation'}
      <div class="flex items-center justify-between mb-2">
        <p class="text-xs font-medium" style="color: var(--color-text-tertiary);">
          Steps to close the gap:
        </p>
        <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold" style="background: var(--color-accent-primary)15; color: var(--color-accent-primary);">
          ~{totalEffortDays} days total · {guidance.effort_estimate}
        </span>
      </div>
      <div class="space-y-1.5">
        {#each guidance.remediation_actions as action, i}
          <div class="flex items-center gap-2 rounded px-3 py-2 text-xs" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
            <span class="font-bold shrink-0 w-4 text-center" style="color: var(--color-accent-primary);">{i + 1}</span>
            <span class="flex-1 font-medium" style="color: var(--color-text-primary);">{action.action}</span>
            <span class="shrink-0 px-1.5 py-0.5 rounded text-[10px]" style="background: var(--color-bg-surface-hover); color: var(--color-text-tertiary);">
              {action.owner_hint}
            </span>
            <span class="shrink-0 text-[10px] font-semibold" style="color: var(--color-accent-primary);">
              {action.effort_days}d
            </span>
          </div>
        {/each}
      </div>

    {:else if activeTab === 'investigate'}
      <p class="text-xs mb-2 font-medium" style="color: var(--color-text-tertiary);">
        Ask your engineering and security team:
      </p>
      <ul class="space-y-1.5">
        {#each guidance.investigation_prompts as prompt}
          <li class="flex items-start gap-2 text-xs" style="color: var(--color-text-secondary);">
            <HelpCircle class="w-3.5 h-3.5 mt-0.5 shrink-0" style="color: var(--color-accent-primary);" />
            {prompt}
          </li>
        {/each}
      </ul>

    {:else if activeTab === 'gaps'}
      <p class="text-xs mb-2 font-medium" style="color: var(--color-text-tertiary);">
        Most teams miss these — check yours:
      </p>
      <ul class="space-y-1.5">
        {#each guidance.common_gaps as gap}
          <li class="flex items-start gap-2 text-xs" style="color: var(--color-text-secondary);">
            <AlertTriangle class="w-3.5 h-3.5 mt-0.5 shrink-0" style="color: var(--color-status-warning);" />
            {gap}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</div>
