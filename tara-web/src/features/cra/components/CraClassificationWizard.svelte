<script lang="ts">
  import type { ClassificationResult, ProductCategory } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { onMount } from 'svelte';
  import { Shield, Search, ChevronLeft, Info, AlertTriangle, Calendar } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    oncomplete?: (result: ClassificationResult) => void;
    oncancel?: () => void;
  }

  let { assessmentId, oncomplete, oncancel }: Props = $props();

  let categories: ProductCategory[] = $state([]);
  let selectedCategoryId: string | null = $state(null);
  let usesHarmonisedStandard: boolean = $state(false);
  let isOpenSourcePublic: boolean = $state(false);
  let autoException: boolean = $state(false);
  let searchQuery: string = $state('');
  let currentStep: number = $state(0);
  let loading: boolean = $state(true);
  let submitting: boolean = $state(false);
  let result: ClassificationResult | null = $state(null);

  const STEP_LABELS = ['Select Category', 'Options', 'Review'] as const;

  const filteredCategories = $derived(
    searchQuery.trim()
      ? categories.filter((c) =>
          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.examples.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : categories
  );

  const groupedCategories = $derived({
    class_i: filteredCategories.filter((c) => c.classification === 'class_i'),
    class_ii: filteredCategories.filter((c) => c.classification === 'class_ii'),
    critical: filteredCategories.filter((c) => c.classification === 'critical'),
  });

  const selectedCategory = $derived(
    categories.find((c) => c.id === selectedCategoryId) ?? null
  );

  onMount(async () => {
    try {
      categories = await craApi.getProductCategories();
    } catch (err) {
      console.error('Failed to load product categories:', err);
    } finally {
      loading = false;
    }
  });

  async function submitClassification(): Promise<void> {
    submitting = true;
    try {
      result = await craApi.classify(assessmentId, {
        category_id: selectedCategoryId ?? undefined,
        uses_harmonised_standard: usesHarmonisedStandard,
        is_open_source_public: isOpenSourcePublic,
        automotive_exception: autoException,
      });
      oncomplete?.(result);
    } catch (err) {
      console.error('Failed to classify:', err);
    } finally {
      submitting = false;
    }
  }

  const CLASSIFICATION_STYLES: Record<string, { color: string; label: string }> = {
    default: { color: 'var(--color-status-info)', label: 'Default' },
    class_i: { color: 'var(--color-status-warning)', label: 'Important Class I' },
    class_ii: { color: 'var(--color-status-error)', label: 'Important Class II' },
    critical: { color: '#dc2626', label: 'Critical' },
  };
</script>

<div class="max-w-2xl mx-auto">
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if result}
    {@const style = CLASSIFICATION_STYLES[result.classification] ?? CLASSIFICATION_STYLES.default}
    <div class="text-center space-y-6 py-8">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full" style="background: {style.color}20;">
        <Shield class="w-8 h-8" style="color: {style.color};" />
      </div>
      <div>
        <h2 class="text-xl font-bold mb-1" style="color: var(--color-text-primary);">{style.label}</h2>
        <p class="text-sm" style="color: var(--color-text-secondary);">{result.category_name}</p>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">{result.rationale}</p>
      </div>
      <div class="grid grid-cols-2 gap-3 text-left max-w-lg mx-auto">
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Conformity Module</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">{result.conformity_module.name}</div>
          {#if result.conformity_module.mandatory}
            <span class="text-[10px] px-1.5 py-0.5 rounded mt-1 inline-block font-bold" style="background: var(--color-status-error)15; color: var(--color-status-error);">NOTIFIED BODY REQUIRED</span>
          {/if}
        </div>
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Full Compliance</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">{result.compliance_deadline}</div>
        </div>
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="flex items-center gap-1">
            <AlertTriangle class="w-3 h-3" style="color: var(--color-status-error);" />
            <span class="text-xs" style="color: var(--color-status-error);">Reporting Deadline</span>
          </div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">{result.reporting_deadline}</div>
        </div>
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Estimated Cost</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">
            €{result.cost_estimate_min.toLocaleString()} – €{result.cost_estimate_max.toLocaleString()}
          </div>
        </div>
      </div>
      <div class="rounded-lg border p-3 text-left max-w-lg mx-auto" style="background: var(--color-accent-primary)05; border-color: var(--color-accent-primary)30;">
        <div class="text-xs font-medium mb-1" style="color: var(--color-accent-primary);">Module Rationale</div>
        <p class="text-xs" style="color: var(--color-text-secondary);">{result.conformity_module.rationale}</p>
      </div>
    </div>
  {:else}
    <div class="space-y-4">
      <!-- Step indicators -->
      <div class="flex items-center gap-1">
        {#each STEP_LABELS as label, i}
          <div class="flex items-center gap-1 flex-1">
            <div class="h-1 flex-1 rounded-full" style="background: {i <= currentStep ? 'var(--color-accent-primary)' : 'var(--color-bg-surface-hover)'};"></div>
          </div>
        {/each}
      </div>
      <div class="text-xs" style="color: var(--color-text-tertiary);">Step {currentStep + 1}: {STEP_LABELS[currentStep]}</div>

      {#if currentStep === 0}
        <!-- Step 1: Category selection -->
        <div class="space-y-3">
          <div class="flex items-center gap-2 rounded-lg border px-3 py-2" style="border-color: var(--color-border-default);">
            <Search class="w-4 h-4" style="color: var(--color-text-tertiary);" />
            <input
              type="text"
              placeholder="Search categories (e.g. router, firewall, HSM...)"
              class="flex-1 bg-transparent outline-none text-sm"
              style="color: var(--color-text-primary);"
              bind:value={searchQuery}
            />
          </div>
          <div class="rounded-lg border p-3 flex items-start gap-2" style="background: var(--color-accent-primary)05; border-color: var(--color-accent-primary)30;">
            <Info class="w-4 h-4 mt-0.5 shrink-0" style="color: var(--color-accent-primary);" />
            <p class="text-xs" style="color: var(--color-text-secondary);">
              Select the category matching your product's <strong>core functionality</strong>. 
              Ancillary features don't count — e.g. a smartphone with a built-in browser is NOT a "browser."
              If none match, your product is <strong>Default</strong> category.
            </p>
          </div>
          <button
            class="w-full text-left rounded-lg border p-3 cursor-pointer transition-all"
            style="background: {selectedCategoryId === null ? 'var(--color-accent-primary)08' : 'var(--color-bg-surface)'}; border-color: {selectedCategoryId === null ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};"
            onclick={() => { selectedCategoryId = null; }}
          >
            <div class="flex items-center justify-between">
              <div>
                <span class="text-sm font-medium" style="color: var(--color-text-primary);">None of the below — Default Category</span>
                <p class="text-xs mt-0.5" style="color: var(--color-text-tertiary);">Module A self-assessment. No notified body needed.</p>
              </div>
              <span class="text-[10px] px-1.5 py-0.5 rounded font-bold" style="background: var(--color-status-info)15; color: var(--color-status-info);">DEFAULT</span>
            </div>
          </button>
          <!-- Class I -->
          {#if groupedCategories.class_i.length > 0}
            <div class="text-xs font-semibold uppercase tracking-wider pt-2" style="color: var(--color-status-warning);">Important — Class I ({groupedCategories.class_i.length})</div>
            <div class="space-y-1 max-h-48 overflow-y-auto">
              {#each groupedCategories.class_i as cat}
                <button
                  class="w-full text-left rounded-lg border p-2.5 cursor-pointer transition-all"
                  style="background: {selectedCategoryId === cat.id ? 'var(--color-status-warning)08' : 'var(--color-bg-surface)'}; border-color: {selectedCategoryId === cat.id ? 'var(--color-status-warning)' : 'var(--color-border-default)'};"
                  onclick={() => { selectedCategoryId = cat.id; }}
                >
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">{cat.name}</div>
                  <div class="text-xs" style="color: var(--color-text-tertiary);">{cat.examples}</div>
                </button>
              {/each}
            </div>
          {/if}
          <!-- Class II -->
          {#if groupedCategories.class_ii.length > 0}
            <div class="text-xs font-semibold uppercase tracking-wider pt-2" style="color: var(--color-status-error);">Important — Class II ({groupedCategories.class_ii.length})</div>
            <div class="space-y-1 max-h-36 overflow-y-auto">
              {#each groupedCategories.class_ii as cat}
                <button
                  class="w-full text-left rounded-lg border p-2.5 cursor-pointer transition-all"
                  style="background: {selectedCategoryId === cat.id ? 'var(--color-status-error)08' : 'var(--color-bg-surface)'}; border-color: {selectedCategoryId === cat.id ? 'var(--color-status-error)' : 'var(--color-border-default)'};"
                  onclick={() => { selectedCategoryId = cat.id; }}
                >
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">{cat.name}</div>
                  <div class="text-xs" style="color: var(--color-text-tertiary);">{cat.examples}</div>
                </button>
              {/each}
            </div>
          {/if}
          <!-- Critical -->
          {#if groupedCategories.critical.length > 0}
            <div class="text-xs font-semibold uppercase tracking-wider pt-2" style="color: #dc2626;">Critical ({groupedCategories.critical.length})</div>
            <div class="space-y-1">
              {#each groupedCategories.critical as cat}
                <button
                  class="w-full text-left rounded-lg border p-2.5 cursor-pointer transition-all"
                  style="background: {selectedCategoryId === cat.id ? '#dc262608' : 'var(--color-bg-surface)'}; border-color: {selectedCategoryId === cat.id ? '#dc2626' : 'var(--color-border-default)'};"
                  onclick={() => { selectedCategoryId = cat.id; }}
                >
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">{cat.name}</div>
                  <div class="text-xs" style="color: var(--color-text-tertiary);">{cat.examples}</div>
                </button>
              {/each}
            </div>
          {/if}
        </div>

      {:else if currentStep === 1}
        <!-- Step 2: Additional options -->
        <div class="space-y-4 py-2">
          <label class="flex items-start gap-3 rounded-lg border p-3 cursor-pointer" style="border-color: var(--color-border-default);">
            <input type="checkbox" class="mt-1" bind:checked={usesHarmonisedStandard} />
            <div>
              <div class="text-sm font-medium" style="color: var(--color-text-primary);">Will you apply a harmonised standard?</div>
              <p class="text-xs mt-0.5" style="color: var(--color-text-tertiary);">
                Class I products applying a harmonised standard can use Module A (self-assessment) instead of third-party assessment.
              </p>
            </div>
          </label>
          <label class="flex items-start gap-3 rounded-lg border p-3 cursor-pointer" style="border-color: var(--color-border-default);">
            <input type="checkbox" class="mt-1" bind:checked={isOpenSourcePublic} />
            <div>
              <div class="text-sm font-medium" style="color: var(--color-text-primary);">Free/open-source with public technical docs?</div>
              <p class="text-xs mt-0.5" style="color: var(--color-text-tertiary);">
                Class I/II open-source products with public technical docs can use Module A per Art. 32(5).
              </p>
            </div>
          </label>
          <label class="flex items-start gap-3 rounded-lg border p-3 cursor-pointer" style="border-color: var(--color-border-default);">
            <input type="checkbox" class="mt-1" bind:checked={autoException} />
            <div>
              <div class="text-sm font-medium" style="color: var(--color-text-primary);">Automotive exception (UN R155)?</div>
              <p class="text-xs mt-0.5" style="color: var(--color-text-tertiary);">
                Product sold exclusively to one OEM for vehicle type-approval under UN R155. CRA may not apply.
              </p>
            </div>
          </label>
        </div>

      {:else}
        <!-- Step 3: Review -->
        <div class="space-y-3 py-2">
          <div class="rounded-lg border p-3" style="border-color: var(--color-border-default);">
            <div class="text-xs" style="color: var(--color-text-tertiary);">Selected Category</div>
            <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">
              {selectedCategory?.name ?? 'Default (no matching category)'}
            </div>
            {#if selectedCategory}
              <span class="text-[10px] px-1.5 py-0.5 rounded mt-1 inline-block font-bold"
                style="background: {CLASSIFICATION_STYLES[selectedCategory.classification]?.color ?? 'gray'}15; color: {CLASSIFICATION_STYLES[selectedCategory.classification]?.color ?? 'gray'};">
                {CLASSIFICATION_STYLES[selectedCategory.classification]?.label ?? selectedCategory.classification}
              </span>
            {:else}
              <span class="text-[10px] px-1.5 py-0.5 rounded mt-1 inline-block font-bold" style="background: var(--color-status-info)15; color: var(--color-status-info);">DEFAULT</span>
            {/if}
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div class="rounded-lg border p-2 text-center" style="border-color: var(--color-border-default);">
              <div class="text-[10px]" style="color: var(--color-text-tertiary);">Harmonised Std</div>
              <div class="text-xs font-medium" style="color: var(--color-text-primary);">{usesHarmonisedStandard ? 'Yes' : 'No'}</div>
            </div>
            <div class="rounded-lg border p-2 text-center" style="border-color: var(--color-border-default);">
              <div class="text-[10px]" style="color: var(--color-text-tertiary);">Open Source</div>
              <div class="text-xs font-medium" style="color: var(--color-text-primary);">{isOpenSourcePublic ? 'Yes' : 'No'}</div>
            </div>
            <div class="rounded-lg border p-2 text-center" style="border-color: var(--color-border-default);">
              <div class="text-[10px]" style="color: var(--color-text-tertiary);">Auto Exception</div>
              <div class="text-xs font-medium" style="color: var(--color-text-primary);">{autoException ? 'Yes' : 'No'}</div>
            </div>
          </div>
        </div>
      {/if}

      <!-- Navigation -->
      <div class="flex items-center justify-between pt-4">
        <button
          class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
          style="color: var(--color-text-secondary);"
          disabled={currentStep === 0}
          onclick={() => { if (currentStep > 0) currentStep--; }}
        >
          <ChevronLeft class="w-3 h-3" />
          Back
        </button>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
            style="color: var(--color-text-tertiary);"
            onclick={() => oncancel?.()}
          >
            Cancel
          </button>
          {#if currentStep < 2}
            <button
              class="px-4 py-1.5 rounded text-xs font-medium cursor-pointer"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              onclick={() => currentStep++}
            >
              Next
            </button>
          {:else}
            <button
              class="px-4 py-1.5 rounded text-xs font-medium cursor-pointer"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              onclick={submitClassification}
              disabled={submitting}
            >
              {submitting ? 'Classifying...' : 'Classify Product'}
            </button>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>
