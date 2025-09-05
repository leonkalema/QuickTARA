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

  function getAFR(afs: number): string {
    if (afs >= 25) return 'Very Low';
    if (afs >= 20) return 'Low';
    if (afs >= 14) return 'Medium';
    if (afs >= 1) return 'High';
    return '–';
  }

  function getNRV(afs: number): number {
    if (afs >= 25) return 0.0;
    if (afs >= 20) return 1.0;
    if (afs >= 14) return 1.5;
    if (afs >= 1) return 2.0;
    return 0.0;
  }

  function getRatingColor(afs: number): string {
    if (afs >= 25) return 'bg-red-500';      // Very Low (NRV: 0.0)
    if (afs >= 20) return 'bg-orange-500';   // Low (NRV: 1.0)
    if (afs >= 14) return 'bg-yellow-500';   // Medium (NRV: 1.5)
    if (afs >= 1) return 'bg-green-500';     // High (NRV: 2.0)
    return 'bg-gray-500';                    // No score
  }

  function getRatingTextColor(afs: number): string {
    if (afs >= 25) return 'text-red-600';
    if (afs >= 20) return 'text-orange-600';
    if (afs >= 14) return 'text-yellow-600';
    if (afs >= 1) return 'text-green-600';
    return 'text-gray-600';
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
    return 'No assessment available - please select values for all feasibility factors.';
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

<div class="space-y-6">
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <h4 class="text-sm font-medium text-blue-900 mb-2">Attack Feasibility Rating</h4>
    <p class="text-sm text-blue-700">Select the appropriate value for each factor. Higher values indicate lower feasibility.</p>
  </div>

  <div class="grid grid-cols-1 gap-6">
    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        Elapsed Time
      </label>
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-2">
        {#each elapsedTimeOptions as option}
          <label class="relative">
            <input
              type="radio"
              bind:group={feasibilityRating.elapsed_time}
              value={option.value}
              class="sr-only"
            />
            <div class="border-2 rounded-lg p-3 cursor-pointer transition-all
                       {feasibilityRating.elapsed_time === option.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}">
              <div class="text-center">
                <div class="text-xs font-medium {feasibilityRating.elapsed_time === option.value ? 'text-blue-700' : 'text-gray-600'}">{option.label}</div>
              </div>
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        Specialist Expertise
      </label>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {#each expertiseOptions as option}
          <label class="relative">
            <input
              type="radio"
              bind:group={feasibilityRating.specialist_expertise}
              value={option.value}
              class="sr-only"
            />
            <div class="border-2 rounded-lg p-3 cursor-pointer transition-all
                       {feasibilityRating.specialist_expertise === option.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}">
              <div class="text-center">
                <div class="text-xs font-medium {feasibilityRating.specialist_expertise === option.value ? 'text-blue-700' : 'text-gray-600'}">{option.label}</div>
              </div>
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        Knowledge of Component
      </label>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {#each knowledgeOptions as option}
          <label class="relative">
            <input
              type="radio"
              bind:group={feasibilityRating.knowledge_of_target}
              value={option.value}
              class="sr-only"
            />
            <div class="border-2 rounded-lg p-3 cursor-pointer transition-all
                       {feasibilityRating.knowledge_of_target === option.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}">
              <div class="text-center">
                <div class="text-xs font-medium {feasibilityRating.knowledge_of_target === option.value ? 'text-blue-700' : 'text-gray-600'}">{option.label}</div>
              </div>
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        Window of Opportunity
      </label>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {#each opportunityOptions as option}
          <label class="relative">
            <input
              type="radio"
              bind:group={feasibilityRating.window_of_opportunity}
              value={option.value}
              class="sr-only"
            />
            <div class="border-2 rounded-lg p-3 cursor-pointer transition-all
                       {feasibilityRating.window_of_opportunity === option.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}">
              <div class="text-center">
                <div class="text-xs font-medium {feasibilityRating.window_of_opportunity === option.value ? 'text-blue-700' : 'text-gray-600'}">{option.label}</div>
              </div>
            </div>
          </label>
        {/each}
      </div>
    </div>

    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        Equipment
      </label>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {#each equipmentOptions as option}
          <label class="relative">
            <input
              type="radio"
              bind:group={feasibilityRating.equipment}
              value={option.value}
              class="sr-only"
            />
            <div class="border-2 rounded-lg p-3 cursor-pointer transition-all
                       {feasibilityRating.equipment === option.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}">
              <div class="text-center">
                <div class="text-xs font-medium {feasibilityRating.equipment === option.value ? 'text-blue-700' : 'text-gray-600'}">{option.label}</div>
              </div>
            </div>
          </label>
        {/each}
      </div>
    </div>
  </div>

  <div class="bg-white border border-gray-300 rounded-lg p-6 shadow-sm">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">Attack Feasibility Assessment</h3>
    
    <!-- Score Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <div class="text-2xl font-bold text-gray-900">{overallRating}</div>
        <div class="text-sm text-gray-600">Attack Feasibility Score (AFS)</div>
        <div class="text-xs text-gray-500 mt-1">Range: 0-57</div>
      </div>
      
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <div class="text-lg font-semibold {getRatingTextColor(overallRating)}">{getAFR(overallRating)}</div>
        <div class="text-sm text-gray-600">Attack Feasibility Rating (AFR)</div>
        <div class="text-xs text-gray-500 mt-1">Qualitative Assessment</div>
      </div>
      
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <div class="text-2xl font-bold text-gray-900">{getNRV(overallRating)}</div>
        <div class="text-sm text-gray-600">Numerical Risk Value (NRV)</div>
        <div class="text-xs text-gray-500 mt-1">Risk Multiplier</div>
      </div>
    </div>

    <!-- Visual Rating Scale -->
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium text-gray-700">Feasibility Level</span>
        <span class="text-sm px-3 py-1 rounded-full text-white {getRatingColor(overallRating)}">{getAFR(overallRating)}</span>
      </div>
      
      <div class="relative">
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div 
            class="h-3 rounded-full transition-all duration-500 {getRatingColor(overallRating)}"
            style="width: {getProgressWidth(overallRating)}%"
          ></div>
        </div>
        
        <!-- Scale markers -->
        <div class="flex justify-between text-xs text-gray-500 mt-2">
          <div class="text-center">
            <div class="w-px h-2 bg-gray-300 mx-auto mb-1"></div>
            <span>0<br>Very High</span>
          </div>
          <div class="text-center">
            <div class="w-px h-2 bg-gray-300 mx-auto mb-1"></div>
            <span>13<br>High</span>
          </div>
          <div class="text-center">
            <div class="w-px h-2 bg-gray-300 mx-auto mb-1"></div>
            <span>19<br>Medium</span>
          </div>
          <div class="text-center">
            <div class="w-px h-2 bg-gray-300 mx-auto mb-1"></div>
            <span>24<br>Low</span>
          </div>
          <div class="text-center">
            <div class="w-px h-2 bg-gray-300 mx-auto mb-1"></div>
            <span>57<br>Very Low</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Rating Explanation -->
    <div class="text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-3">
      <div class="font-medium text-blue-800 mb-1">Assessment Interpretation:</div>
      <div>{getRatingExplanation(overallRating)}</div>
    </div>
  </div>
</div>
