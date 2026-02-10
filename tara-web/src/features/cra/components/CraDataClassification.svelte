<script lang="ts">
  import { onMount } from 'svelte';
  import type { DataProfileQuestion, DataProfile, ApplicabilityResult } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { Database, CheckCircle, XCircle, AlertTriangle, Save, Info } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    onupdate?: () => void;
  }

  let { assessmentId, onupdate }: Props = $props();

  let questions: DataProfileQuestion[] = $state([]);
  let answers: Record<string, boolean> = $state({});
  let applicability: ApplicabilityResult[] = $state([]);
  let autoResolvedCount: number = $state(0);
  let loading = $state(true);
  let saving = $state(false);
  let saved = $state(false);
  let hasProfile = $state(false);

  const CATEGORY_ORDER = ['Storage', 'Privacy', 'Connectivity', 'Access', 'Lifecycle', 'Supply Chain', 'Cryptography'] as const;

  let groupedQuestions = $derived(
    CATEGORY_ORDER
      .map(cat => ({ category: cat, items: questions.filter(q => q.category === cat) }))
      .filter(g => g.items.length > 0)
  );

  let applicableCount = $derived(applicability.filter(a => a.applicable).length);
  let naCount = $derived(applicability.filter(a => !a.applicable).length);

  onMount(async () => {
    try {
      const [qs, profile] = await Promise.all([
        craApi.getDataClassificationQuestions(),
        craApi.getDataProfile(assessmentId),
      ]);
      questions = qs;
      if (Object.keys(profile.profile).length > 0) {
        answers = { ...profile.profile };
        applicability = [...profile.applicability];
        autoResolvedCount = profile.auto_resolved_count;
        hasProfile = true;
      } else {
        for (const q of qs) {
          answers[q.key] = false;
        }
      }
    } catch (err) {
      console.error('Failed to load data classification:', err);
    } finally {
      loading = false;
    }
  });

  function toggleAnswer(key: string): void {
    answers[key] = !answers[key];
    saved = false;
  }

  async function saveProfile(): Promise<void> {
    saving = true;
    saved = false;
    try {
      const result = await craApi.updateDataProfile(assessmentId, answers as DataProfile);
      applicability = [...result.applicability];
      autoResolvedCount = result.auto_resolved_count;
      hasProfile = true;
      saved = true;
      onupdate?.();
    } catch (err) {
      console.error('Failed to save data profile:', err);
    } finally {
      saving = false;
    }
  }
</script>

{#if loading}
  <div class="flex items-center justify-center py-12">
    <div class="animate-spin rounded-full h-6 w-6 border-2" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
  </div>
{:else}
  <div class="space-y-5">
    <!-- Header -->
    <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
      <div class="flex items-center gap-2 mb-2">
        <Database class="w-4 h-4" style="color: var(--color-accent-primary);" />
        <h3 class="text-sm font-bold" style="color: var(--color-text-primary);">Product Data Profile</h3>
      </div>
      <p class="text-xs leading-relaxed" style="color: var(--color-text-tertiary);">
        Answer these questions about your product. Requirements that don't apply based on your answers
        will be automatically marked as <strong>Not Applicable</strong> with a justification.
      </p>
    </div>

    <!-- Questions by category -->
    {#each groupedQuestions as group (group.category)}
      <div>
        <h4 class="text-xs font-semibold uppercase tracking-wider mb-2 px-1" style="color: var(--color-text-tertiary);">
          {group.category}
        </h4>
        <div class="space-y-2">
          {#each group.items as q (q.key)}
            <button
              class="w-full text-left rounded-lg border p-3 transition-colors cursor-pointer"
              style="
                background: {answers[q.key] ? 'var(--color-accent-primary)08' : 'var(--color-bg-surface)'};
                border-color: {answers[q.key] ? 'var(--color-accent-primary)40' : 'var(--color-border-default)'};
              "
              onclick={() => toggleAnswer(q.key)}
            >
              <div class="flex items-center justify-between gap-3">
                <div class="flex-1">
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">{q.label}</div>
                  <div class="text-xs mt-0.5" style="color: var(--color-text-tertiary);">{q.help_text}</div>
                </div>
                <div
                  class="shrink-0 w-10 h-5 rounded-full relative transition-colors"
                  style="background: {answers[q.key] ? 'var(--color-accent-primary)' : 'var(--color-bg-surface-hover)'};"
                >
                  <div
                    class="absolute top-0.5 w-4 h-4 rounded-full transition-all"
                    style="
                      background: {answers[q.key] ? '#fff' : 'var(--color-text-tertiary)'};
                      left: {answers[q.key] ? '22px' : '2px'};
                    "
                  ></div>
                </div>
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/each}

    <!-- Save button -->
    <div class="flex items-center gap-3">
      <button
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={saveProfile}
        disabled={saving}
      >
        <Save class="w-3.5 h-3.5" />
        {saving ? 'Saving...' : 'Save & Analyze'}
      </button>
      {#if saved}
        <span class="flex items-center gap-1 text-xs font-medium" style="color: var(--color-status-success);">
          <CheckCircle class="w-3.5 h-3.5" />
          Profile saved — {autoResolvedCount} requirements auto-resolved
        </span>
      {/if}
    </div>

    <!-- Applicability results -->
    {#if hasProfile && applicability.length > 0}
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-bold" style="color: var(--color-text-primary);">Requirement Applicability</h4>
          <div class="flex items-center gap-3 text-xs">
            <span class="flex items-center gap-1" style="color: var(--color-status-success);">
              <CheckCircle class="w-3 h-3" /> {applicableCount} apply
            </span>
            <span class="flex items-center gap-1" style="color: var(--color-text-tertiary);">
              <XCircle class="w-3 h-3" /> {naCount} N/A
            </span>
          </div>
        </div>
        <div class="space-y-1.5">
          {#each applicability as result (result.requirement_id)}
            <div
              class="flex items-start gap-2 px-3 py-2 rounded text-xs"
              style="background: {result.applicable ? 'transparent' : 'var(--color-status-success)08'};"
            >
              {#if result.applicable}
                <AlertTriangle class="w-3 h-3 mt-0.5 shrink-0" style="color: var(--color-status-warning);" />
              {:else}
                <CheckCircle class="w-3 h-3 mt-0.5 shrink-0" style="color: var(--color-status-success);" />
              {/if}
              <div>
                <span class="font-semibold" style="color: var(--color-text-primary);">{result.requirement_id}</span>
                <span style="color: {result.applicable ? 'var(--color-text-secondary)' : 'var(--color-status-success)'};">
                  — {result.justification}
                </span>
              </div>
            </div>
          {/each}
        </div>
      </div>

      {#if naCount > 0}
        <div class="flex items-start gap-2 px-3 py-2 rounded-lg text-xs" style="background: var(--color-accent-primary)08; border: 1px solid var(--color-accent-primary)20;">
          <Info class="w-3.5 h-3.5 mt-0.5 shrink-0" style="color: var(--color-accent-primary);" />
          <span style="color: var(--color-text-secondary);">
            {naCount} requirements were marked <strong>Not Applicable</strong> based on your data profile.
            The compliance percentage has been updated. Switch to the Requirements tab to see the changes.
          </span>
        </div>
      {/if}
    {/if}
  </div>
{/if}
