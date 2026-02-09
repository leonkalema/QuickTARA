<script lang="ts">
  import type { ClassificationQuestion, ClassificationResult, ClassificationQuestionsResponse } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { onMount } from 'svelte';
  import { Shield, ChevronRight, ChevronLeft, Check } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    oncomplete?: (result: ClassificationResult) => void;
    oncancel?: () => void;
  }

  let { assessmentId, oncomplete, oncancel }: Props = $props();

  let questions: ClassificationQuestion[] = $state([]);
  let autoExceptionQuestion: ClassificationQuestion | null = $state(null);
  let answers: Record<string, boolean> = $state({});
  let autoException: boolean = $state(false);
  let currentStep = $state(0);
  let loading = $state(true);
  let submitting = $state(false);
  let result: ClassificationResult | null = $state(null);

  const TOTAL_STEPS = $derived(questions.length + 1);
  const isLastQuestion = $derived(currentStep === questions.length);
  const currentQuestion = $derived(
    currentStep < questions.length ? questions[currentStep] : autoExceptionQuestion
  );

  onMount(async () => {
    try {
      const data: ClassificationQuestionsResponse = await craApi.getClassificationQuestions();
      questions = data.questions;
      autoExceptionQuestion = data.automotive_exception_question;
      questions.forEach((q) => { answers[q.id] = false; });
    } catch (err) {
      console.error('Failed to load questions:', err);
    } finally {
      loading = false;
    }
  });

  function answerQuestion(value: boolean): void {
    if (currentQuestion) {
      if (isLastQuestion) {
        autoException = value;
      } else {
        answers[currentQuestion.id] = value;
      }
    }
    if (currentStep < TOTAL_STEPS - 1) {
      currentStep++;
    }
  }

  function goBack(): void {
    if (currentStep > 0) currentStep--;
  }

  async function submitClassification(): Promise<void> {
    submitting = true;
    try {
      result = await craApi.classify(assessmentId, {
        answers,
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
    <!-- Result screen -->
    {@const style = CLASSIFICATION_STYLES[result.classification] ?? CLASSIFICATION_STYLES.default}
    <div class="text-center space-y-6 py-8">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full" style="background: {style.color}20;">
        <Shield class="w-8 h-8" style="color: {style.color};" />
      </div>
      <div>
        <h2 class="text-xl font-bold mb-1" style="color: var(--color-text-primary);">
          {style.label}
        </h2>
        <p class="text-sm" style="color: var(--color-text-secondary);">{result.rationale}</p>
      </div>
      <div class="grid grid-cols-2 gap-4 text-left max-w-md mx-auto">
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Conformity Assessment</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">{result.conformity_assessment}</div>
        </div>
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Compliance Deadline</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">{result.compliance_deadline}</div>
        </div>
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Estimated Cost</div>
          <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">
            €{result.cost_estimate_min.toLocaleString()} – €{result.cost_estimate_max.toLocaleString()}
          </div>
        </div>
        {#if result.automotive_exception}
          <div class="rounded-lg border p-3" style="background: var(--color-status-warning)10; border-color: var(--color-status-warning);">
            <div class="text-xs" style="color: var(--color-status-warning);">Automotive Exception</div>
            <div class="text-sm font-medium mt-1" style="color: var(--color-text-primary);">Potentially excluded (lex specialis)</div>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <!-- Wizard steps -->
    <div class="space-y-6">
      <!-- Progress bar -->
      <div class="flex items-center gap-1">
        {#each Array(TOTAL_STEPS) as _, i}
          <div
            class="h-1 flex-1 rounded-full transition-all duration-300"
            style="background: {i <= currentStep ? 'var(--color-accent-primary)' : 'var(--color-bg-surface-hover)'};"
          ></div>
        {/each}
      </div>

      <div class="text-xs" style="color: var(--color-text-tertiary);">
        Question {currentStep + 1} of {TOTAL_STEPS}
      </div>

      {#if currentQuestion}
        <div class="py-4">
          <h3 class="text-lg font-semibold mb-2" style="color: var(--color-text-primary);">
            {currentQuestion.text}
          </h3>
          <p class="text-sm" style="color: var(--color-text-tertiary);">
            {currentQuestion.hint}
          </p>
        </div>

        <div class="flex gap-3">
          <button
            class="flex-1 py-3 rounded-lg border text-sm font-medium transition-all cursor-pointer"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-status-success)'; }}
            onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-default)'; }}
            onclick={() => answerQuestion(true)}
          >
            <Check class="w-4 h-4 inline mr-1" style="color: var(--color-status-success);" />
            Yes
          </button>
          <button
            class="flex-1 py-3 rounded-lg border text-sm font-medium transition-all cursor-pointer"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-status-error)'; }}
            onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-default)'; }}
            onclick={() => answerQuestion(false)}
          >
            No
          </button>
        </div>
      {/if}

      <!-- Navigation -->
      <div class="flex items-center justify-between pt-4">
        <button
          class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
          style="color: var(--color-text-secondary);"
          disabled={currentStep === 0}
          onclick={goBack}
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
          {#if currentStep === TOTAL_STEPS - 1}
            <button
              class="px-4 py-1.5 rounded text-xs font-medium cursor-pointer"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              onclick={submitClassification}
              disabled={submitting}
            >
              {submitting ? 'Classifying...' : 'Submit Classification'}
            </button>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>
