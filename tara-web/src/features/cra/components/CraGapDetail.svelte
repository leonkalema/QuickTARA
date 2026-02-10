<script lang="ts">
  import type { GapRequirementItem, CompensatingControlCatalogItem } from '$lib/types/cra';
  import { AlertTriangle, Shield, Check, Loader2, Plus, Clock, Wrench } from '@lucide/svelte';

  interface Props {
    gap: GapRequirementItem;
    riskColor: string;
    isLegacy: boolean;
    catalog: CompensatingControlCatalogItem[];
    onapplycontrol: (gap: GapRequirementItem, controlId: string) => void;
    applyingControlId: string | null;
    appliedFlash: string | null;
  }

  let { gap, riskColor, isLegacy, catalog, onapplycontrol, applyingControlId, appliedFlash }: Props = $props();

  function getCatalogItem(controlId: string): CompensatingControlCatalogItem | undefined {
    return catalog.find((c: CompensatingControlCatalogItem) => c.control_id === controlId);
  }

  function getControlName(controlId: string): string {
    return getCatalogItem(controlId)?.name ?? controlId;
  }

  function isAlreadyApplied(controlId: string): boolean {
    return gap.applied_controls.some(c => c.control_id === controlId);
  }
</script>

<div class="px-4 pb-4 pt-2 ml-7 space-y-3 border-l-2" style="border-color: {riskColor};">
  <!-- Meta row -->
  <div class="flex flex-wrap gap-3 text-xs" style="color: var(--color-text-secondary);">
    <span><strong>Article:</strong> {gap.guidance?.cra_article ?? gap.article}</span>
    {#if gap.guidance?.priority}
      <span><strong>Priority:</strong> {gap.guidance.priority}</span>
    {/if}
    {#if gap.owner}
      <span><strong>Owner:</strong> {gap.owner}</span>
    {/if}
    {#if gap.target_date}
      <span><strong>Target:</strong> {gap.target_date}</span>
    {/if}
  </div>
  {#if gap.guidance?.deadline_note}
    <div class="flex items-center gap-1.5 text-[11px] px-2 py-1 rounded" style="background: var(--color-status-warning)10; color: var(--color-status-warning);">
      <Clock class="w-3 h-3 shrink-0" />
      {gap.guidance.deadline_note}
    </div>
  {/if}
  <!-- Explanation -->
  {#if gap.guidance?.explanation}
    <p class="text-xs leading-relaxed" style="color: var(--color-text-secondary);">
      {gap.guidance.explanation}
    </p>
  {/if}
  <!-- Sub-requirements -->
  {#if gap.guidance?.sub_requirements && gap.guidance.sub_requirements.length > 0}
    <div>
      <div class="text-xs font-semibold mb-1.5" style="color: var(--color-text-primary);">Sub-Requirements to Check</div>
      <div class="space-y-1.5">
        {#each gap.guidance.sub_requirements as sub, i}
          <div class="rounded border px-2.5 py-1.5" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
            <div class="text-xs font-medium" style="color: var(--color-text-primary);">
              <span class="font-bold" style="color: var(--color-accent-primary);">{i + 1}.</span> {sub.description}
            </div>
            <div class="flex gap-4 mt-0.5 text-[10px]">
              <span style="color: var(--color-status-success);"><strong>Evidence:</strong> {sub.check_evidence}</span>
            </div>
            <div class="text-[10px] mt-0.5" style="color: var(--color-status-warning);">
              <strong>Typical gap:</strong> {sub.typical_gap}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
  <!-- Common gaps -->
  {#if gap.guidance?.common_gaps && gap.guidance.common_gaps.length > 0}
    <div>
      <div class="text-xs font-semibold mb-1" style="color: var(--color-status-warning);">Common Gaps for {gap.requirement_id}</div>
      <ul class="space-y-0.5">
        {#each gap.guidance.common_gaps as g}
          <li class="flex items-start gap-1.5 text-[11px]" style="color: var(--color-text-secondary);">
            <AlertTriangle class="w-3 h-3 mt-0.5 shrink-0" style="color: var(--color-status-warning);" />
            {g}
          </li>
        {/each}
      </ul>
    </div>
  {/if}
  <!-- Remediation actions -->
  {#if gap.guidance?.remediation_actions && gap.guidance.remediation_actions.length > 0}
    <div>
      <div class="flex items-center justify-between mb-1.5">
        <div class="text-xs font-semibold flex items-center gap-1" style="color: var(--color-accent-primary);">
          <Wrench class="w-3 h-3" /> Remediation Steps
        </div>
        {#if gap.guidance.effort_estimate}
          <span class="text-[10px] px-1.5 py-0.5 rounded" style="background: var(--color-accent-primary)10; color: var(--color-accent-primary);">
            {gap.guidance.effort_estimate}
          </span>
        {/if}
      </div>
      <div class="space-y-1">
        {#each gap.guidance.remediation_actions as action, i}
          <div class="flex items-center gap-2 text-[11px] px-2 py-1.5 rounded" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
            <span class="font-bold shrink-0 w-3 text-center" style="color: var(--color-accent-primary);">{i + 1}</span>
            <span class="flex-1" style="color: var(--color-text-primary);">{action.action}</span>
            <span class="shrink-0 px-1 py-0.5 rounded text-[9px]" style="background: var(--color-bg-surface-hover); color: var(--color-text-tertiary);">
              {action.owner_hint}
            </span>
            <span class="shrink-0 text-[10px] font-semibold" style="color: var(--color-accent-primary);">{action.effort_days}d</span>
          </div>
        {/each}
      </div>
    </div>
  {/if}
  <!-- Applied controls -->
  {#if gap.applied_controls.length > 0}
    <div>
      <div class="text-xs font-medium mb-1" style="color: var(--color-accent-primary);">Applied Controls</div>
      <div class="flex flex-wrap gap-2">
        {#each gap.applied_controls as ctrl}
          <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary)15; color: var(--color-accent-primary);">
            <Shield class="w-3 h-3" />
            {ctrl.name}
            <span style="color: var(--color-text-tertiary);">({ctrl.status})</span>
          </span>
        {/each}
      </div>
    </div>
  {/if}
  <!-- Suggested controls (legacy only) -->
  {#if gap.suggested_controls.length > 0 && isLegacy}
    {@const unapplied = gap.suggested_controls.filter(cid => !isAlreadyApplied(cid))}
    {#if unapplied.length > 0}
      <div>
        <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Apply a Control to Reduce Risk</div>
        <div class="flex flex-wrap gap-2">
          {#each unapplied as controlId}
            {@const key = `${gap.requirement_id}:${controlId}`}
            {@const isApplying = applyingControlId === key}
            {@const justApplied = appliedFlash === key}
            <button
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer transition-all"
              style="background: {justApplied ? 'var(--color-status-success)15' : 'var(--color-bg-surface-hover)'}; color: {justApplied ? 'var(--color-status-success)' : 'var(--color-accent-primary)'}; border: 1px solid {justApplied ? 'var(--color-status-success)' : 'var(--color-accent-primary)30'};"
              onclick={() => onapplycontrol(gap, controlId)}
              disabled={isApplying}
            >
              {#if isApplying}
                <Loader2 class="w-3 h-3 animate-spin" />
                Applying...
              {:else if justApplied}
                <Check class="w-3 h-3" />
                Applied!
              {:else}
                <Plus class="w-3 h-3" />
                {getControlName(controlId)}
              {/if}
            </button>
          {/each}
        </div>
      </div>
    {/if}
  {:else if !isLegacy && gap.applied_controls.length === 0}
    <div class="flex items-center gap-2 text-xs" style="color: var(--color-text-tertiary);">
      <AlertTriangle class="w-3 h-3" />
      <span>Requires direct implementation — update status in Requirements tab when done</span>
    </div>
  {/if}
  <!-- Standards & TARA evidence -->
  <div class="flex flex-wrap gap-3 text-[10px] pt-1 border-t" style="border-color: var(--color-border-subtle);">
    {#if gap.guidance?.mapped_standards && gap.guidance.mapped_standards.length > 0}
      <span style="color: var(--color-text-tertiary);">
        <strong>Standards:</strong> {gap.guidance.mapped_standards.join(', ')}
      </span>
    {/if}
    {#if gap.tara_evidence.length > 0}
      <span style="color: var(--color-accent-primary);">
        TARA: {gap.tara_evidence[0].count} {gap.tara_evidence[0].type}(s) linked
      </span>
    {/if}
  </div>
</div>
