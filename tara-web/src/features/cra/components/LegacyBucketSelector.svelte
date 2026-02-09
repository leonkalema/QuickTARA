<script lang="ts">
  import { Check, X, AlertTriangle, Code, Wrench, Archive } from '@lucide/svelte';
  import type { CraProductType } from '$lib/types/cra';

  interface Props {
    onselect: (bucket: CraProductType) => void;
    oncancel: () => void;
  }

  const { onselect, oncancel }: Props = $props();

  interface BucketQuestion {
    id: string;
    text: string;
    hint: string;
  }

  const BUCKET_QUESTIONS: BucketQuestion[] = [
    {
      id: 'source_code',
      text: 'Do you have access to the product source code?',
      hint: 'Full source code access enables proper TARA, SBOM generation, and patching.',
    },
    {
      id: 'can_patch',
      text: 'Can you release software updates for this product?',
      hint: 'Ability to patch vulnerabilities through OTA or service updates.',
    },
    {
      id: 'active_support',
      text: 'Is this product still under active development/support?',
      hint: 'Engineering resources available for security fixes.',
    },
  ];

  interface BucketInfo {
    type: CraProductType;
    name: string;
    description: string;
    icon: typeof Code;
    color: string;
    requirements: string[];
  }

  const BUCKET_INFO: Record<string, BucketInfo> = {
    legacy_a: {
      type: 'legacy_a',
      name: 'Bucket A — Maintainable',
      description: 'Source available, can patch, active support',
      icon: Code,
      color: 'var(--color-status-success)',
      requirements: [
        'Create lightweight TARA',
        'Generate SBOM from source',
        'Standard update process',
        'Full PSIRT integration',
      ],
    },
    legacy_b: {
      type: 'legacy_b',
      name: 'Bucket B — Partial',
      description: 'Limited source or patching capability',
      icon: Wrench,
      color: 'var(--color-status-warning)',
      requirements: [
        'Create minimal TARA',
        'Reconstruct SBOM via binary analysis',
        'Patch where feasible',
        'Full PSIRT + limitations documented',
      ],
    },
    legacy_c: {
      type: 'legacy_c',
      name: 'Bucket C — Orphaned',
      description: 'No source, cannot patch',
      icon: Archive,
      color: 'var(--color-status-error)',
      requirements: [
        'Risk acceptance documentation',
        'SBOM via binary analysis',
        'Compensating controls (Art. 5(3))',
        'Publish End-of-Security-Support date',
        'Technical Justification Memo required',
      ],
    },
  };

  let answers: Record<string, boolean | null> = $state({
    source_code: null,
    can_patch: null,
    active_support: null,
  });

  let step: 'questions' | 'result' = $state('questions');

  const allAnswered = $derived(
    Object.values(answers).every((v) => v !== null)
  );

  const determinedBucket = $derived.by(() => {
    if (!allAnswered) return null;

    const hasSource = answers.source_code;
    const canPatch = answers.can_patch;
    const activeSupport = answers.active_support;

    if (hasSource && canPatch && activeSupport) {
      return 'legacy_a';
    } else if (hasSource || canPatch) {
      return 'legacy_b';
    } else {
      return 'legacy_c';
    }
  });

  function setAnswer(questionId: string, value: boolean): void {
    answers = { ...answers, [questionId]: value };
  }

  function showResult(): void {
    if (determinedBucket) {
      step = 'result';
    }
  }

  function confirmSelection(): void {
    if (determinedBucket) {
      onselect(determinedBucket as CraProductType);
    }
  }

  function selectDifferentBucket(bucket: CraProductType): void {
    onselect(bucket);
  }
</script>

<div class="space-y-6">
  <div>
    <h3 class="text-base font-semibold mb-1" style="color: var(--color-text-primary);">
      Legacy Product Classification
    </h3>
    <p class="text-sm" style="color: var(--color-text-secondary);">
      Answer these questions to determine the appropriate legacy bucket for your product.
    </p>
  </div>

  {#if step === 'questions'}
    <div class="space-y-4">
      {#each BUCKET_QUESTIONS as question}
        <div
          class="rounded-lg border p-4"
          style="background: var(--color-bg-surface); border-color: var(--color-border-default);"
        >
          <div class="text-sm font-medium mb-1" style="color: var(--color-text-primary);">
            {question.text}
          </div>
          <div class="text-xs mb-3" style="color: var(--color-text-tertiary);">
            {question.hint}
          </div>
          <div class="flex gap-2">
            <button
              class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded text-sm font-medium cursor-pointer transition-colors"
              style="
                background: {answers[question.id] === true ? 'var(--color-status-success)15' : 'var(--color-bg-surface-hover)'};
                color: {answers[question.id] === true ? 'var(--color-status-success)' : 'var(--color-text-secondary)'};
                border: 1px solid {answers[question.id] === true ? 'var(--color-status-success)' : 'var(--color-border-default)'};
              "
              onclick={() => setAnswer(question.id, true)}
            >
              <Check class="w-4 h-4" />
              Yes
            </button>
            <button
              class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded text-sm font-medium cursor-pointer transition-colors"
              style="
                background: {answers[question.id] === false ? 'var(--color-status-error)15' : 'var(--color-bg-surface-hover)'};
                color: {answers[question.id] === false ? 'var(--color-status-error)' : 'var(--color-text-secondary)'};
                border: 1px solid {answers[question.id] === false ? 'var(--color-status-error)' : 'var(--color-border-default)'};
              "
              onclick={() => setAnswer(question.id, false)}
            >
              <X class="w-4 h-4" />
              No
            </button>
          </div>
        </div>
      {/each}
    </div>

    <div class="flex justify-between pt-2">
      <button
        class="px-4 py-2 text-sm cursor-pointer"
        style="color: var(--color-text-secondary);"
        onclick={oncancel}
      >
        Cancel
      </button>
      <button
        class="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-colors"
        style="
          background: {allAnswered ? 'var(--color-accent-primary)' : 'var(--color-bg-surface-hover)'};
          color: {allAnswered ? 'var(--color-text-inverse)' : 'var(--color-text-tertiary)'};
        "
        disabled={!allAnswered}
        onclick={showResult}
      >
        Determine Bucket
      </button>
    </div>

  {:else if step === 'result' && determinedBucket}
    {@const bucket = BUCKET_INFO[determinedBucket]}
    <div
      class="rounded-lg border p-5"
      style="background: {bucket.color}08; border-color: {bucket.color};"
    >
      <div class="flex items-start gap-4">
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center"
          style="background: {bucket.color}15;"
        >
          <bucket.icon class="w-6 h-6" style="color: {bucket.color};" />
        </div>
        <div class="flex-1">
          <div class="text-lg font-semibold" style="color: {bucket.color};">
            {bucket.name}
          </div>
          <div class="text-sm mt-1" style="color: var(--color-text-secondary);">
            {bucket.description}
          </div>
          <div class="mt-3">
            <div class="text-xs font-medium uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">
              CRA Requirements for this bucket:
            </div>
            <ul class="space-y-1">
              {#each bucket.requirements as req}
                <li class="text-xs flex items-center gap-2" style="color: var(--color-text-secondary);">
                  <span class="w-1 h-1 rounded-full" style="background: {bucket.color};"></span>
                  {req}
                </li>
              {/each}
            </ul>
          </div>
        </div>
      </div>
    </div>

    {#if determinedBucket === 'legacy_c'}
      <div
        class="rounded-lg border p-3 flex items-start gap-2"
        style="background: var(--color-status-warning)10; border-color: var(--color-status-warning);"
      >
        <AlertTriangle class="w-4 h-4 mt-0.5 flex-shrink-0" style="color: var(--color-status-warning);" />
        <div class="text-xs" style="color: var(--color-text-secondary);">
          <strong style="color: var(--color-status-warning);">Bucket C products require compensating controls.</strong>
          You'll need to document Art. 5(3) justification and specify alternative measures since patching isn't feasible.
        </div>
      </div>
    {/if}

    <div class="flex justify-between pt-2">
      <button
        class="px-4 py-2 text-sm cursor-pointer"
        style="color: var(--color-text-secondary);"
        onclick={() => { step = 'questions'; }}
      >
        ← Re-answer Questions
      </button>
      <button
        class="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={confirmSelection}
      >
        Use {bucket.name.split(' — ')[0]}
      </button>
    </div>

    <!-- Override option -->
    <div class="border-t pt-4 mt-4" style="border-color: var(--color-border-default);">
      <div class="text-xs mb-2" style="color: var(--color-text-tertiary);">
        Need a different bucket? Select manually:
      </div>
      <div class="flex gap-2">
        {#each Object.values(BUCKET_INFO) as b}
          {#if b.type !== determinedBucket}
            <button
              class="flex-1 px-3 py-2 rounded text-xs cursor-pointer"
              style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
              onclick={() => selectDifferentBucket(b.type)}
            >
              {b.name.split(' — ')[0]}
            </button>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
</div>
