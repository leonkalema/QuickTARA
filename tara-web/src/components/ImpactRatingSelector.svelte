<script lang="ts">
  import type { ImpactRating } from '../lib/types/damageScenario';
  
  export let impactRating: ImpactRating;
  export let disabled = false;
  
  const levels = [
    { value: 'negligible', label: 'Negligible', color: 'bg-green-100 text-green-800' },
    { value: 'moderate', label: 'Moderate', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'major', label: 'Major', color: 'bg-orange-100 text-orange-800' },
    { value: 'severe', label: 'Severe', color: 'bg-red-100 text-red-800' }
  ];
  
  function getLevelColor(level: string) {
    return levels.find(l => l.value === level)?.color || 'bg-gray-100 text-gray-800';
  }
</script>

<div class="space-y-3">
  <div class="grid grid-cols-2 gap-4">
    <!-- Safety Impact -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Safety</label>
      <select 
        bind:value={impactRating.safety} 
        {disabled}
        class="w-full text-sm border-gray-300 rounded-md {getLevelColor(impactRating.safety)}"
      >
        {#each levels as level}
          <option value={level.value}>{level.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Financial Impact -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Financial</label>
      <select 
        bind:value={impactRating.financial} 
        {disabled}
        class="w-full text-sm border-gray-300 rounded-md {getLevelColor(impactRating.financial)}"
      >
        {#each levels as level}
          <option value={level.value}>{level.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Operational Impact -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Operational</label>
      <select 
        bind:value={impactRating.operational} 
        {disabled}
        class="w-full text-sm border-gray-300 rounded-md {getLevelColor(impactRating.operational)}"
      >
        {#each levels as level}
          <option value={level.value}>{level.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Privacy Impact -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Privacy</label>
      <select 
        bind:value={impactRating.privacy} 
        {disabled}
        class="w-full text-sm border-gray-300 rounded-md {getLevelColor(impactRating.privacy)}"
      >
        {#each levels as level}
          <option value={level.value}>{level.label}</option>
        {/each}
      </select>
    </div>
  </div>
</div>
