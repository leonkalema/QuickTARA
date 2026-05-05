<script lang="ts">
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type { ConformityChecklist } from '$lib/types/cra';

  export let assessmentId: string;

  let checklist: ConformityChecklist | null = null;
  let loading = true;
  let error = '';
  let saving = false;

  // Editing state per step
  let editing: Record<string, boolean> = {};

  onMount(async () => {
    try {
      checklist = await craApi.getConformityChecklist(assessmentId);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'Failed to load checklist';
    } finally {
      loading = false;
    }
  });

  async function toggle(field: keyof ConformityChecklist) {
    if (!checklist || saving) return;
    saving = true;
    try {
      checklist = await craApi.updateConformityChecklist(assessmentId, {
        [field]: !checklist[field],
      });
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'Save failed';
    } finally {
      saving = false;
    }
  }

  async function saveField(field: string, value: string) {
    if (!checklist || saving) return;
    saving = true;
    try {
      checklist = await craApi.updateConformityChecklist(assessmentId, {
        [field]: value || null,
      });
      editing[field] = false;
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'Save failed';
    } finally {
      saving = false;
    }
  }

  $: progressPct = checklist ? Math.round((checklist.completed_steps / checklist.total_steps) * 100) : 0;
  $: progressColor = progressPct === 100 ? 'bg-green-500' : progressPct >= 50 ? 'bg-yellow-400' : 'bg-red-400';
</script>

<div class="bg-white border border-gray-200 rounded-lg p-6">
  <div class="flex items-center justify-between mb-4">
    <div>
      <h3 class="text-lg font-semibold text-gray-900">Art. 13 Conformity Obligations</h3>
      <p class="text-sm text-gray-500 mt-0.5">
        Track the procedural compliance acts required beyond Annex I — Art. 13, 28, 31 CRA
      </p>
    </div>
    {#if checklist}
      <div class="text-right">
        <span class="text-2xl font-bold text-gray-900">{checklist.completed_steps}/{checklist.total_steps}</span>
        <p class="text-xs text-gray-500">steps done</p>
      </div>
    {/if}
  </div>

  {#if checklist}
    <!-- Progress bar -->
    <div class="w-full bg-gray-100 rounded-full h-2 mb-6">
      <div class="{progressColor} h-2 rounded-full transition-all duration-300" style="width: {progressPct}%"></div>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-8 text-gray-400">Loading checklist…</div>
  {:else if error}
    <div class="text-red-600 text-sm py-4">{error}</div>
  {:else if checklist}
    <div class="space-y-4">

      <!-- Step 1: Conformity Assessment -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.conformity_assessment_done ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.conformity_assessment_done ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('conformity_assessment_done')}
            disabled={saving}
          >
            {#if checklist.conformity_assessment_done}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">Conformity assessment completed</span>
              <span class="text-xs text-gray-400 font-mono">Art. 32</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Complete the conformity assessment procedure (Module A self-assessment, or Module B+C / H with notified body).
            </p>
            {#if checklist.conformity_assessment_done}
              <div class="mt-2 flex flex-wrap gap-3 text-sm text-gray-600">
                {#if checklist.conformity_assessment_module}
                  <span>Module: <strong>{checklist.conformity_assessment_module}</strong></span>
                {/if}
                {#if checklist.conformity_assessment_date}
                  <span>Date: <strong>{checklist.conformity_assessment_date}</strong></span>
                {/if}
              </div>
            {/if}
            {#if editing['conformity_assessment_module']}
              <div class="mt-2 flex gap-2">
                <input
                  type="text"
                  class="border rounded px-2 py-1 text-sm flex-1"
                  placeholder="e.g. Module A, Module B+C"
                  value={checklist.conformity_assessment_module ?? ''}
                  on:blur={(e) => saveField('conformity_assessment_module', (e.target as HTMLInputElement).value)}
                />
              </div>
            {:else}
              <button class="mt-1 text-xs text-blue-500 hover:underline" on:click={() => editing['conformity_assessment_module'] = true}>
                {checklist.conformity_assessment_module ? 'Edit module' : '+ Add module'}
              </button>
            {/if}
          </div>
        </div>
      </div>

      <!-- Step 2: EU Declaration of Conformity -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.doc_signed ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.doc_signed ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('doc_signed')}
            disabled={saving}
          >
            {#if checklist.doc_signed}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">EU Declaration of Conformity (DoC) signed</span>
              <span class="text-xs text-gray-400 font-mono">Art. 28 / Annex V</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Draw up and sign the EU Declaration of Conformity per Annex V. Must be kept for 10 years.
            </p>
            {#if checklist.doc_signed}
              <div class="mt-2 flex flex-wrap gap-3 text-sm text-gray-600">
                {#if checklist.doc_signatory}
                  <span>Signatory: <strong>{checklist.doc_signatory}</strong></span>
                {/if}
                {#if checklist.doc_signed_date}
                  <span>Signed: <strong>{checklist.doc_signed_date}</strong></span>
                {/if}
                {#if checklist.doc_storage_location}
                  <span>Stored: <strong>{checklist.doc_storage_location}</strong></span>
                {/if}
              </div>
            {/if}
            {#if editing['doc_signatory']}
              <div class="mt-2 flex gap-2">
                <input
                  type="text"
                  class="border rounded px-2 py-1 text-sm flex-1"
                  placeholder="Name / role of signatory"
                  value={checklist.doc_signatory ?? ''}
                  on:blur={(e) => saveField('doc_signatory', (e.target as HTMLInputElement).value)}
                />
              </div>
            {:else}
              <button class="mt-1 text-xs text-blue-500 hover:underline" on:click={() => editing['doc_signatory'] = true}>
                {checklist.doc_signatory ? 'Edit signatory' : '+ Add signatory'}
              </button>
            {/if}
          </div>
        </div>
      </div>

      <!-- Step 3: CE Marking -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.ce_marking_applied ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.ce_marking_applied ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('ce_marking_applied')}
            disabled={saving}
          >
            {#if checklist.ce_marking_applied}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">CE marking affixed</span>
              <span class="text-xs text-gray-400 font-mono">Art. 28–30</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Affix the CE marking on the product, packaging, or accompanying documents. Must be visible and legible.
            </p>
            {#if checklist.ce_marking_date}
              <p class="text-sm text-gray-600 mt-1">Date: <strong>{checklist.ce_marking_date}</strong></p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Step 4: EU Registration -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.eu_registration_done ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.eu_registration_done ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('eu_registration_done')}
            disabled={saving}
          >
            {#if checklist.eu_registration_done}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">Product registered in EU central database</span>
              <span class="text-xs text-gray-400 font-mono">Art. 31</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Register the product in the ENISA-administered EU database before placing on the EU market.
              Class I, II, and Critical products must register. Default products are exempt.
            </p>
            {#if checklist.eu_registration_id}
              <p class="text-sm text-gray-600 mt-1">Registration ID: <strong>{checklist.eu_registration_id}</strong></p>
            {/if}
            {#if editing['eu_registration_id']}
              <div class="mt-2 flex gap-2">
                <input
                  type="text"
                  class="border rounded px-2 py-1 text-sm flex-1"
                  placeholder="EU database registration ID"
                  value={checklist.eu_registration_id ?? ''}
                  on:blur={(e) => saveField('eu_registration_id', (e.target as HTMLInputElement).value)}
                />
              </div>
            {:else}
              <button class="mt-1 text-xs text-blue-500 hover:underline" on:click={() => editing['eu_registration_id'] = true}>
                {checklist.eu_registration_id ? 'Edit ID' : '+ Add registration ID'}
              </button>
            {/if}
          </div>
        </div>
      </div>

      <!-- Step 5: 10-year Retention Plan -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.retention_plan_confirmed ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.retention_plan_confirmed ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('retention_plan_confirmed')}
            disabled={saving}
          >
            {#if checklist.retention_plan_confirmed}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">10-year technical documentation retention confirmed</span>
              <span class="text-xs text-gray-400 font-mono">Art. 23(1)</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Technical documentation (Annex VII), DoC, and test results must be retained for at least
              10 years after the product is placed on the market (or the product's support period, whichever is longer).
            </p>
          </div>
        </div>
      </div>

      <!-- Step 6: Post-Market Surveillance -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.post_market_plan_confirmed ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.post_market_plan_confirmed ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('post_market_plan_confirmed')}
            disabled={saving}
          >
            {#if checklist.post_market_plan_confirmed}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">Post-market surveillance plan in place</span>
              <span class="text-xs text-gray-400 font-mono">Art. 13(14)</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              Maintain a process for monitoring the product after market placement: CVE tracking,
              incident response, update management, and corrective action procedures.
            </p>
          </div>
        </div>
      </div>

      <!-- Step 7: EOSS Published -->
      <div class="border border-gray-100 rounded-lg p-4 {checklist.eoss_published ? 'bg-green-50 border-green-200' : 'bg-white'}">
        <div class="flex items-start gap-3">
          <button
            class="mt-0.5 w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors {checklist.eoss_published ? 'bg-green-500 border-green-500' : 'border-gray-300'}"
            on:click={() => toggle('eoss_published')}
            disabled={saving}
          >
            {#if checklist.eoss_published}
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
              </svg>
            {/if}
          </button>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">End-of-support date published to users</span>
              <span class="text-xs text-gray-400 font-mono">Art. 14(2) / Annex II §5</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              The support period end date must be communicated clearly to users — on the product page,
              in the manual, and on the manufacturer's website. Required from 11 Sep 2026.
            </p>
            {#if checklist.eoss_published_url}
              <p class="text-sm text-gray-600 mt-1">
                URL: <a href={checklist.eoss_published_url} target="_blank" class="text-blue-500 hover:underline">{checklist.eoss_published_url}</a>
              </p>
            {/if}
            {#if editing['eoss_published_url']}
              <div class="mt-2 flex gap-2">
                <input
                  type="url"
                  class="border rounded px-2 py-1 text-sm flex-1"
                  placeholder="https://example.com/support-period"
                  value={checklist.eoss_published_url ?? ''}
                  on:blur={(e) => saveField('eoss_published_url', (e.target as HTMLInputElement).value)}
                />
              </div>
            {:else}
              <button class="mt-1 text-xs text-blue-500 hover:underline" on:click={() => editing['eoss_published_url'] = true}>
                {checklist.eoss_published_url ? 'Edit URL' : '+ Add URL'}
              </button>
            {/if}
          </div>
        </div>
      </div>

    </div>

    {#if progressPct === 100}
      <div class="mt-5 bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
        All Art. 13 conformity obligations confirmed. Product is ready for market placement.
      </div>
    {/if}
  {/if}
</div>
