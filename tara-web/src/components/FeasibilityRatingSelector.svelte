<script lang="ts">
  import type { FeasibilityRating } from '../lib/types/attackPath';
  
  export let feasibilityRating: FeasibilityRating;
  export let disabled = false;

  const ratingLabels = {
    1: 'Very Low',
    2: 'Low', 
    3: 'Medium',
    4: 'High'
  };

  const ratingDescriptions = {
    elapsed_time: {
      1: '< 1 day',
      2: '< 1 week', 
      3: '< 1 month',
      4: '> 1 month'
    },
    specialist_expertise: {
      1: 'Layman',
      2: 'Proficient',
      3: 'Expert', 
      4: 'Multiple Experts'
    },
    knowledge_of_target: {
      1: 'Public',
      2: 'Restricted',
      3: 'Confidential',
      4: 'Critical'
    },
    window_of_opportunity: {
      1: 'Unnecessary / Unlimited',
      2: 'Easy',
      3: 'Moderate',
      4: 'Difficult'
    },
    equipment: {
      1: 'Standard',
      2: 'Specialized',
      3: 'Bespoke',
      4: 'Multiple Bespoke'
    }
  };

  const factors = [
    { key: 'elapsed_time', label: 'Elapsed Time' },
    { key: 'specialist_expertise', label: 'Specialist Expertise' },
    { key: 'knowledge_of_target', label: 'Knowledge of Target' },
    { key: 'window_of_opportunity', label: 'Window of Opportunity' },
    { key: 'equipment', label: 'Equipment' }
  ];

  // Calculate overall rating when individual ratings change
  $: {
    const total = feasibilityRating.elapsed_time + 
                  feasibilityRating.specialist_expertise + 
                  feasibilityRating.knowledge_of_target + 
                  feasibilityRating.window_of_opportunity + 
                  feasibilityRating.equipment;
    feasibilityRating.overall_rating = Math.round((total / 5) * 10) / 10;
  }
</script>

<div class="space-y-6">
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <h4 class="text-sm font-medium text-blue-900 mb-2">Feasibility Rating Scale</h4>
    <p class="text-sm text-blue-700">Rate each factor from 1 (easiest for attacker) to 4 (most difficult for attacker)</p>
  </div>

  <div class="grid grid-cols-1 gap-6">
    {#each factors as factor}
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700">
          {factor.label}
        </label>
        
        <div class="grid grid-cols-4 gap-2">
          {#each [1, 2, 3, 4] as rating}
            <label class="relative">
              <input
                type="radio"
                bind:group={feasibilityRating[factor.key]}
                value={rating}
                {disabled}
                class="sr-only peer"
              />
              <div class="border-2 border-gray-200 rounded-lg p-3 cursor-pointer transition-all
                         peer-checked:border-slate-500 peer-checked:bg-slate-50
                         hover:border-gray-300 peer-disabled:cursor-not-allowed peer-disabled:opacity-50">
                <div class="text-center">
                  <div class="text-lg font-semibold text-gray-900">{rating}</div>
                  <div class="text-xs font-medium text-gray-600 mt-1">{ratingLabels[rating]}</div>
                  <div class="text-xs text-gray-500 mt-1">{ratingDescriptions[factor.key][rating]}</div>
                </div>
              </div>
            </label>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  {#if feasibilityRating.overall_rating}
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Overall Feasibility Rating</span>
        <div class="flex items-center space-x-2">
          <span class="text-lg font-bold text-gray-900">{feasibilityRating.overall_rating}</span>
          <span class="text-sm text-gray-500">/ 4.0</span>
        </div>
      </div>
      <div class="mt-2">
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="h-2 rounded-full transition-all duration-300 {feasibilityRating.overall_rating <= 1.5 ? 'bg-green-500' : feasibilityRating.overall_rating <= 2.5 ? 'bg-yellow-500' : feasibilityRating.overall_rating <= 3.5 ? 'bg-orange-500' : 'bg-red-500'}"
            style="width: {(feasibilityRating.overall_rating / 4) * 100}%"
          ></div>
        </div>
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Easy to Execute</span>
          <span>Difficult to Execute</span>
        </div>
      </div>
    </div>
  {/if}
</div>
