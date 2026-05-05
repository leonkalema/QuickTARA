<script lang="ts">
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type { AnnexIIChecklist, AnnexIIItem } from '$lib/types/cra';

  export let assessmentId: string;

  let checklist: AnnexIIChecklist | null = null;
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      checklist = await craApi.getAnnexIIChecklist(assessmentId);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'Failed to load checklist';
    } finally {
      loading = false;
    }
  });

  function statusLabel(item: AnnexIIItem): string {
    if (item.status === 'done') return 'Done';
    if (item.status === 'action_required') return 'Action required';
    return 'Not checked';
  }

  function statusClasses(item: AnnexIIItem): string {
    if (item.status === 'done') return 'bg-green-100 text-green-800';
    if (item.status === 'action_required') return 'bg-red-100 text-red-700';
    return 'bg-gray-100 text-gray-600';
  }

  function rowClasses(item: AnnexIIItem): string {
    if (item.status === 'done') return 'border-green-100 bg-green-50';
    if (item.status === 'action_required') return 'border-red-100 bg-red-50';
    return 'border-gray-100 bg-white';
  }

  $: doneCount = checklist?.done_count ?? 0;
  $: totalCount = checklist?.total_count ?? 9;
  $: progressPct = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;
</script>

<div class="bg-white border border-gray-200 rounded-lg p-6">
  <div class="flex items-center justify-between mb-4">
    <div>
      <h3 class="text-lg font-semibold text-gray-900">Annex II — User Information Requirements</h3>
      <p class="text-sm text-gray-500 mt-0.5">
        Mandatory information manufacturers must provide to users — Art. 13(20) and Annex II CRA
      </p>
    </div>
    {#if checklist}
      <div class="text-right">
        <span class="text-2xl font-bold text-gray-900">{doneCount}/{totalCount}</span>
        <p class="text-xs text-gray-500">confirmed</p>
      </div>
    {/if}
  </div>

  {#if checklist}
    <div class="w-full bg-gray-100 rounded-full h-2 mb-1">
      <div
        class="{progressPct === 100 ? 'bg-green-500' : progressPct > 0 ? 'bg-blue-400' : 'bg-gray-200'} h-2 rounded-full transition-all duration-300"
        style="width: {progressPct}%"
      ></div>
    </div>
    <p class="text-xs text-gray-400 mb-5">
      Items auto-derived from assessment data are marked with a lock icon.
      All others must be confirmed manually in your product documentation.
    </p>
  {/if}

  {#if loading}
    <div class="text-center py-8 text-gray-400">Loading Annex II checklist…</div>
  {:else if error}
    <div class="text-red-600 text-sm py-4">{error}</div>
  {:else if checklist}
    <div class="space-y-3">
      {#each checklist.items as item, i (item.key)}
        <div class="border rounded-lg p-4 {rowClasses(item)}">
          <div class="flex items-start gap-3">
            <!-- Index -->
            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-white border border-gray-200 flex items-center justify-center text-xs font-mono text-gray-500 mt-0.5">
              {i + 1}
            </span>

            <div class="flex-1 min-w-0">
              <div class="flex items-center flex-wrap gap-2">
                <span class="font-medium text-gray-900 text-sm">{item.title}</span>
                <span class="text-xs font-mono text-gray-400">{item.article_ref}</span>
                {#if item.auto_derived}
                  <span title="Auto-derived from assessment data" class="text-gray-400">
                    <svg class="w-3.5 h-3.5 inline" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
                    </svg>
                  </span>
                {/if}
                <span class="text-xs px-2 py-0.5 rounded-full font-medium {statusClasses(item)}">
                  {statusLabel(item)}
                </span>
              </div>

              <p class="text-sm text-gray-500 mt-1">{item.description}</p>

              {#if item.status === 'done' && item.derived_value}
                <p class="text-xs text-green-700 mt-1">
                  Derived value: <strong>{item.derived_value}</strong>
                </p>
              {/if}

              {#if item.status === 'action_required'}
                <div class="mt-2 bg-red-50 border border-red-200 rounded px-3 py-2 text-xs text-red-700">
                  Set the <strong>End-of-Support date</strong> in the assessment settings to fulfil this requirement automatically.
                </div>
              {/if}

              {#if item.status === 'not_checked'}
                <p class="mt-1 text-xs text-gray-400 italic">
                  Verify this is covered in your product documentation, packaging, and/or website.
                </p>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>

    {#if doneCount === 0}
      <div class="mt-5 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
        <strong>Note:</strong> None of the Annex II items are auto-confirmed yet. Most require manual
        review of your product documentation. Set the End-of-Support (EOSS) date in the assessment
        settings to auto-confirm item 5.
      </div>
    {/if}
  {/if}
</div>
