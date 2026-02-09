<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { craApi } from '$lib/api/craApi';
  import { productApi } from '$lib/api/productApi';
  import type { CraAssessmentListItem, CraProductType } from '$lib/types/cra';
  import type { Product } from '$lib/types/product';
  import CraAssessmentCard from '../../features/cra/components/CraAssessmentCard.svelte';
  import LegacyBucketSelector from '../../features/cra/components/LegacyBucketSelector.svelte';
  import { Plus, Shield, Search, Zap, Archive, HelpCircle } from '@lucide/svelte';

  let assessments: CraAssessmentListItem[] = $state([]);
  let products: Product[] = $state([]);
  let loading = $state(true);
  let error: string | null = $state(null);
  let showCreateModal = $state(false);
  let selectedProductId = $state('');
  let selectedProductType: CraProductType = $state('current');
  let creating = $state(false);
  let searchQuery = $state('');
  let createStep: 'select-type' | 'select-bucket' | 'confirm' = $state('select-type');
  let isLegacyFlow = $state(false);

  const filteredAssessments = $derived(
    searchQuery
      ? assessments.filter((a) =>
          (a.product_name ?? '').toLowerCase().includes(searchQuery.toLowerCase())
        )
      : assessments
  );

  onMount(async () => {
    await loadData();
  });

  async function loadData(): Promise<void> {
    loading = true;
    error = null;
    try {
      const [assessmentRes, productRes] = await Promise.all([
        craApi.listAssessments(),
        productApi.getAll(),
      ]);
      assessments = assessmentRes.assessments;
      const assessedProductIds = new Set(assessments.map((a) => a.product_id));
      products = (productRes.scopes ?? []).filter(
        (p: Product) => !assessedProductIds.has(p.scope_id)
      );
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load data';
    } finally {
      loading = false;
    }
  }

  async function createAssessment(): Promise<void> {
    if (!selectedProductId) return;
    creating = true;
    try {
      const assessment = await craApi.createAssessment({
        product_id: selectedProductId,
        product_type: selectedProductType,
      });
      closeCreateModal();
      await goto(`/cra/${assessment.id}`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create assessment';
    } finally {
      creating = false;
    }
  }

  function closeCreateModal(): void {
    showCreateModal = false;
    createStep = 'select-type';
    selectedProductId = '';
    selectedProductType = 'current';
    isLegacyFlow = false;
  }

  function selectProductType(type: 'current' | 'legacy'): void {
    if (type === 'current') {
      selectedProductType = 'current';
      isLegacyFlow = false;
      createStep = 'confirm';
    } else {
      isLegacyFlow = true;
      createStep = 'select-bucket';
    }
  }

  function onBucketSelected(bucket: CraProductType): void {
    selectedProductType = bucket;
    createStep = 'confirm';
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold flex items-center gap-2" style="color: var(--color-text-primary);">
        <Shield class="w-5 h-5" style="color: var(--color-accent-primary);" />
        CRA Compliance
      </h1>
      <p class="text-sm mt-1" style="color: var(--color-text-tertiary);">
        EU Cyber Resilience Act assessments across your products
      </p>
    </div>
    <button
      class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-colors"
      style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
      onclick={() => { showCreateModal = true; }}
    >
      <Plus class="w-4 h-4" />
      New Assessment
    </button>
  </div>

  <!-- Search -->
  <div class="relative">
    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color: var(--color-text-tertiary);" />
    <input
      type="text"
      class="w-full pl-10 pr-4 py-2 rounded-lg border text-sm"
      style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
      placeholder="Search assessments..."
      bind:value={searchQuery}
    />
  </div>

  <!-- Content -->
  {#if loading}
    <div class="flex items-center justify-center py-16">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if error}
    <div class="rounded-lg border p-4 text-sm" style="background: var(--color-status-error)10; border-color: var(--color-status-error); color: var(--color-status-error);">
      {error}
    </div>
  {:else if filteredAssessments.length === 0}
    <div class="text-center py-16">
      <Shield class="w-12 h-12 mx-auto mb-3" style="color: var(--color-text-tertiary);" />
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No CRA assessments yet</h3>
      <p class="text-xs" style="color: var(--color-text-tertiary);">Create your first assessment to start tracking CRA compliance.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each filteredAssessments as assessment (assessment.id)}
        <CraAssessmentCard
          {assessment}
          onclick={() => goto(`/cra/${assessment.id}`)}
        />
      {/each}
    </div>
  {/if}
</div>

<!-- Create Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <button class="absolute inset-0 bg-black/50" aria-label="Close modal" onclick={closeCreateModal}></button>
    <div class="relative rounded-xl border p-6 w-full max-w-lg shadow-xl" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">

      {#if createStep === 'select-type'}
        <!-- Step 1: Select product and type -->
        <h2 class="text-lg font-bold mb-4" style="color: var(--color-text-primary);">New CRA Assessment</h2>

        <div class="mb-5">
          <label for="create-product" class="block text-sm font-medium mb-1" style="color: var(--color-text-secondary);">Product</label>
          <select
            id="create-product"
            class="w-full px-3 py-2 rounded-lg border text-sm"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            bind:value={selectedProductId}
          >
            <option value="">Select a product...</option>
            {#each products as product}
              <option value={product.scope_id}>{product.name}</option>
            {/each}
          </select>
        </div>

        <div class="text-sm font-medium mb-3" style="color: var(--color-text-secondary);">Product Type</div>
        <div class="grid grid-cols-2 gap-3">
          <button
            class="p-4 rounded-lg border text-left cursor-pointer transition-colors"
            style="background: var(--color-bg-surface-hover); border-color: var(--color-border-default);"
            onclick={() => selectProductType('current')}
            disabled={!selectedProductId}
          >
            <div class="flex items-center gap-2 mb-2">
              <Zap class="w-5 h-5" style="color: var(--color-accent-primary);" />
              <span class="font-medium" style="color: var(--color-text-primary);">Current Product</span>
            </div>
            <p class="text-xs" style="color: var(--color-text-tertiary);">
              Has existing TARA work. CRA requirements can be auto-linked from your threat analysis.
            </p>
          </button>
          <button
            class="p-4 rounded-lg border text-left cursor-pointer transition-colors"
            style="background: var(--color-bg-surface-hover); border-color: var(--color-border-default);"
            onclick={() => selectProductType('legacy')}
            disabled={!selectedProductId}
          >
            <div class="flex items-center gap-2 mb-2">
              <Archive class="w-5 h-5" style="color: var(--color-status-warning);" />
              <span class="font-medium" style="color: var(--color-text-primary);">Legacy Product</span>
            </div>
            <p class="text-xs" style="color: var(--color-text-tertiary);">
              Older product with limited documentation. We'll help determine the right compliance path.
            </p>
          </button>
        </div>

        <div class="flex justify-end mt-6">
          <button
            class="px-4 py-2 text-sm cursor-pointer"
            style="color: var(--color-text-secondary);"
            onclick={closeCreateModal}
          >
            Cancel
          </button>
        </div>

      {:else if createStep === 'select-bucket'}
        <!-- Step 2: Legacy bucket selection -->
        <LegacyBucketSelector
          onselect={onBucketSelected}
          oncancel={() => { createStep = 'select-type'; }}
        />

      {:else if createStep === 'confirm'}
        <!-- Step 3: Confirm and create -->
        <h2 class="text-lg font-bold mb-4" style="color: var(--color-text-primary);">Confirm Assessment</h2>

        <div class="rounded-lg border p-4 space-y-3" style="background: var(--color-bg-surface-hover); border-color: var(--color-border-default);">
          <div class="flex justify-between">
            <span class="text-sm" style="color: var(--color-text-tertiary);">Product</span>
            <span class="text-sm font-medium" style="color: var(--color-text-primary);">
              {products.find(p => p.scope_id === selectedProductId)?.name ?? selectedProductId}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm" style="color: var(--color-text-tertiary);">Type</span>
            <span class="text-sm font-medium" style="color: var(--color-text-primary);">
              {#if selectedProductType === 'current'}
                Current Product
              {:else if selectedProductType === 'legacy_a'}
                Legacy A — Maintainable
              {:else if selectedProductType === 'legacy_b'}
                Legacy B — Partial
              {:else}
                Legacy C — Orphaned
              {/if}
            </span>
          </div>
        </div>

        {#if selectedProductType === 'current'}
          <div class="mt-4 p-3 rounded-lg border flex items-start gap-2" style="background: var(--color-accent-primary)10; border-color: var(--color-accent-primary);">
            <HelpCircle class="w-4 h-4 mt-0.5 flex-shrink-0" style="color: var(--color-accent-primary);" />
            <p class="text-xs" style="color: var(--color-text-secondary);">
              After creating, use <strong>"Link to TARA"</strong> to automatically map your existing threat analysis to CRA requirements.
            </p>
          </div>
        {:else if selectedProductType === 'legacy_c'}
          <div class="mt-4 p-3 rounded-lg border flex items-start gap-2" style="background: var(--color-status-warning)10; border-color: var(--color-status-warning);">
            <HelpCircle class="w-4 h-4 mt-0.5 flex-shrink-0" style="color: var(--color-status-warning);" />
            <p class="text-xs" style="color: var(--color-text-secondary);">
              Bucket C requires <strong>compensating controls</strong> and Art. 5(3) justification. You'll be guided through this after creation.
            </p>
          </div>
        {/if}

        <div class="flex justify-between mt-6">
          <button
            class="px-4 py-2 text-sm cursor-pointer"
            style="color: var(--color-text-secondary);"
            onclick={() => { createStep = isLegacyFlow ? 'select-bucket' : 'select-type'; }}
          >
            ← Back
          </button>
          <button
            class="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
            style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
            onclick={createAssessment}
            disabled={creating}
          >
            {creating ? 'Creating...' : 'Create Assessment'}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
