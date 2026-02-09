<script lang="ts">
  import type { FeasibilityRating } from '../lib/types/attackPath';

  export let feasibilityRating: FeasibilityRating = {
    elapsed_time: 0,
    specialist_expertise: 0,
    knowledge_of_target: 0,
    window_of_opportunity: 0,
    equipment: 0
  };

  $: overallRating = (
    feasibilityRating.elapsed_time + 
    feasibilityRating.specialist_expertise + 
    feasibilityRating.knowledge_of_target + 
    feasibilityRating.window_of_opportunity + 
    feasibilityRating.equipment
  );

  $: feasibilityRating.overall_rating = overallRating;
  $: rs = getRatingStyle(overallRating);

  function getAFR(afs: number): string {
    if (afs >= 25) return 'Very Low';
    if (afs >= 20) return 'Low';
    if (afs >= 14) return 'Medium';
    if (afs >= 1) return 'High';
    return 'Very High';
  }

  function getNRV(afs: number): number {
    if (afs >= 25) return 0.0;
    if (afs >= 20) return 1.0;
    if (afs >= 14) return 1.5;
    if (afs >= 1) return 2.0;
    return 0.0;
  }

  function getRatingStyle(afs: number): { bg: string; fg: string } {
    if (afs >= 25) return { bg: 'var(--color-risk-low-bg)', fg: 'var(--color-risk-low)' };
    if (afs >= 20) return { bg: 'var(--color-risk-medium-bg)', fg: 'var(--color-risk-medium)' };
    if (afs >= 14) return { bg: 'var(--color-risk-high-bg)', fg: 'var(--color-risk-high)' };
    if (afs >= 1) return { bg: 'var(--color-risk-critical-bg)', fg: 'var(--color-risk-critical)' };
    return { bg: 'var(--color-bg-elevated)', fg: 'var(--color-text-tertiary)' };
  }

  function getProgressWidth(afs: number): number {
    // Invert the progress - higher AFS means lower feasibility
    return Math.max(0, Math.min(100, 100 - (afs / 57) * 100));
  }

  function getRatingExplanation(afs: number): string {
    if (afs >= 25) return 'Attack requires significant resources, expertise, and time. Very difficult to execute successfully.';
    if (afs >= 20) return 'Attack requires considerable effort and specialized knowledge. Moderately difficult to execute.';
    if (afs >= 14) return 'Attack requires some specialized knowledge or equipment. Moderate difficulty level.';
    if (afs >= 1) return 'Attack can be executed with readily available resources and basic knowledge. Relatively easy to perform.';
    return 'Attack can be executed with minimal effort and standard equipment. Extremely easy to perform.';
  }

  const elapsedTimeOptions = [
    { value: 0, label: '≤1 day' },
    { value: 1, label: '≤1 week' },
    { value: 4, label: '≤1 month' },
    { value: 17, label: '≤6 months' },
    { value: 19, label: '>6 months' }
  ];

  const expertiseOptions = [
    { value: 0, label: 'Layman' },
    { value: 3, label: 'Proficient' },
    { value: 6, label: 'Expert' },
    { value: 8, label: 'Multiple experts' }
  ];

  const knowledgeOptions = [
    { value: 0, label: 'Public' },
    { value: 3, label: 'Restricted' },
    { value: 7, label: 'Confidential' },
    { value: 11, label: 'Strictly confidential' }
  ];

  const opportunityOptions = [
    { value: 0, label: 'Unlimited' },
    { value: 1, label: 'Easy' },
    { value: 4, label: 'Moderate' },
    { value: 10, label: 'Difficult/none' }
  ];

  const equipmentOptions = [
    { value: 0, label: 'Standard' },
    { value: 4, label: 'Specialized' },
    { value: 7, label: 'Bespoke' },
    { value: 9, label: 'Multiple bespoke' }
  ];
</script>

<div class="space-y-4">
  <div class="rounded-md p-3" style="background: var(--color-info-bg); border: 1px solid var(--color-info);">
    <p class="text-xs" style="color: var(--color-text-secondary);">Select the appropriate value for each factor. Higher values = lower feasibility.</p>
  </div>

  <div class="space-y-4">
    <div class="space-y-2">
      <span class="block text-xs font-medium" style="color: var(--color-text-secondary);">Elapsed Time</span>
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-1.5">
        {#each elapsedTimeOptions as option}
          <label class="relative cursor-pointer">
            <input type="radio" bind:group={feasibilityRating.elapsed_time} value={option.value} class="sr-only" />
            <div class="rounded-md p-2.5 text-center transition-all text-xs font-medium"
              style="border: 1px solid {feasibilityRating.elapsed_time === option.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}; background: {feasibilityRating.elapsed_time === option.value ? 'var(--color-accent-primary)' : 'var(--color-bg-inset)'}; color: {feasibilityRating.elapsed_time === option.value ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};">
              {option.label}
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-2">
      <span class="block text-xs font-medium" style="color: var(--color-text-secondary);">Specialist Expertise</span>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-1.5">
        {#each expertiseOptions as option}
          <label class="relative cursor-pointer">
            <input type="radio" bind:group={feasibilityRating.specialist_expertise} value={option.value} class="sr-only" />
            <div class="rounded-md p-2.5 text-center transition-all text-xs font-medium"
              style="border: 1px solid {feasibilityRating.specialist_expertise === option.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}; background: {feasibilityRating.specialist_expertise === option.value ? 'var(--color-accent-primary)' : 'var(--color-bg-inset)'}; color: {feasibilityRating.specialist_expertise === option.value ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};">
              {option.label}
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-2">
      <span class="block text-xs font-medium" style="color: var(--color-text-secondary);">Knowledge of Component</span>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-1.5">
        {#each knowledgeOptions as option}
          <label class="relative cursor-pointer">
            <input type="radio" bind:group={feasibilityRating.knowledge_of_target} value={option.value} class="sr-only" />
            <div class="rounded-md p-2.5 text-center transition-all text-xs font-medium"
              style="border: 1px solid {feasibilityRating.knowledge_of_target === option.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}; background: {feasibilityRating.knowledge_of_target === option.value ? 'var(--color-accent-primary)' : 'var(--color-bg-inset)'}; color: {feasibilityRating.knowledge_of_target === option.value ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};">
              {option.label}
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-2">
      <span class="block text-xs font-medium" style="color: var(--color-text-secondary);">Window of Opportunity</span>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-1.5">
        {#each opportunityOptions as option}
          <label class="relative cursor-pointer">
            <input type="radio" bind:group={feasibilityRating.window_of_opportunity} value={option.value} class="sr-only" />
            <div class="rounded-md p-2.5 text-center transition-all text-xs font-medium"
              style="border: 1px solid {feasibilityRating.window_of_opportunity === option.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}; background: {feasibilityRating.window_of_opportunity === option.value ? 'var(--color-accent-primary)' : 'var(--color-bg-inset)'}; color: {feasibilityRating.window_of_opportunity === option.value ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};">
              {option.label}
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-2">
      <span class="block text-xs font-medium" style="color: var(--color-text-secondary);">Equipment</span>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-1.5">
        {#each equipmentOptions as option}
          <label class="relative cursor-pointer">
            <input type="radio" bind:group={feasibilityRating.equipment} value={option.value} class="sr-only" />
            <div class="rounded-md p-2.5 text-center transition-all text-xs font-medium"
              style="border: 1px solid {feasibilityRating.equipment === option.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}; background: {feasibilityRating.equipment === option.value ? 'var(--color-accent-primary)' : 'var(--color-bg-inset)'}; color: {feasibilityRating.equipment === option.value ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};">
              {option.label}
            </div>
          </label>
        {/each}
      </div>
    </div>
  </div>

  <div class="rounded-md p-4 text-center" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h3 class="text-xs font-semibold uppercase tracking-wider mb-3" style="color: var(--color-text-tertiary);">Attack Feasibility Rating</h3>
    <div class="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold mb-3"
      style="background: {rs.bg}; color: {rs.fg};">
      {getAFR(overallRating)}
    </div>
    <p class="text-xs max-w-sm mx-auto" style="color: var(--color-text-tertiary);">
      {getRatingExplanation(overallRating)}
    </p>
  </div>
</div>
