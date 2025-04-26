<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import type { MitigationStrategy } from '../../api/threat';
  import { 
    createThreatCatalogItem, 
    getThreatCatalogItem, 
    updateThreatCatalogItem, 
    StrideCategory,
    ComponentType,
    TrustZone,
    AttackVector,
    type ThreatCatalogCreate,
    type ThreatCatalogUpdate
  } from '../../api/threat';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  
  export let threatId: string | null = null;
  export let mode: 'create' | 'edit' = 'create';
  
  const dispatch = createEventDispatcher();
  
  // Form state
  let title = '';
  let description = '';
  let strideCategory = StrideCategory.SPOOFING;
  let componentTypes: ComponentType[] = [];
  let trustZones: TrustZone[] = [];
  let attackVectors: AttackVector[] = [];
  let prerequisites: string[] = '';
  let typicalLikelihood = 3;
  let typicalSeverity = 3;
  let cweIds: string = '';
  let capecIds: string = '';
  let examples: string = '';
  let mitigationStrategies: MitigationStrategy[] = [createEmptyMitigationStrategy()];
  
  let loading = false;
  let submitting = false;
  let error = '';
  
  // Create an empty mitigation strategy
  function createEmptyMitigationStrategy(): MitigationStrategy {
    return {
      title: '',
      description: '',
      effectiveness: 3,
      implementation_complexity: 3,
      references: []
    };
  }
  
  // Add a new mitigation strategy
  function addMitigationStrategy() {
    mitigationStrategies = [...mitigationStrategies, createEmptyMitigationStrategy()];
  }
  
  // Remove a mitigation strategy
  function removeMitigationStrategy(index: number) {
    mitigationStrategies = mitigationStrategies.filter((_, i) => i !== index);
  }
  
  // Update a mitigation strategy field
  function updateMitigationStrategy(index: number, field: string, value: any) {
    mitigationStrategies = mitigationStrategies.map((strategy, i) => {
      if (i === index) {
        return { ...strategy, [field]: value };
      }
      return strategy;
    });
  }
  
  // Update mitigation strategy references
  function updateReferences(index: number, value: string) {
    const references = value.split(',').map(ref => ref.trim()).filter(ref => ref);
    updateMitigationStrategy(index, 'references', references);
  }
  
  // Convert array to string for form display
  function arrayToString(arr: string[]): string {
    return arr.join(', ');
  }
  
  // Convert string to array for API submission
  function stringToArray(str: string): string[] {
    return str.split(',').map(item => item.trim()).filter(item => item);
  }
  
  // Handle form submission
  async function handleSubmit() {
    if (!title || !description) {
      showNotification('Title and description are required', 'error');
      return;
    }
    
    submitting = true;
    error = '';
    
    try {
      // Convert form data to API format
      const formData: ThreatCatalogCreate | ThreatCatalogUpdate = {
        title,
        description,
        stride_category: strideCategory,
        applicable_component_types: componentTypes,
        applicable_trust_zones: trustZones,
        attack_vectors: attackVectors,
        prerequisites: stringToArray(prerequisites),
        typical_likelihood: typicalLikelihood,
        typical_severity: typicalSeverity,
        mitigation_strategies: mitigationStrategies.filter(ms => ms.title && ms.description),
        cwe_ids: stringToArray(cweIds),
        capec_ids: stringToArray(capecIds),
        examples: stringToArray(examples)
      };
      
      let result;
      if (mode === 'create') {
        result = await createThreatCatalogItem(formData as ThreatCatalogCreate);
        dispatch('created', result);
      } else if (mode === 'edit' && threatId) {
        result = await updateThreatCatalogItem(threatId, formData as ThreatCatalogUpdate);
        dispatch('updated', result);
      }
    } catch (err) {
      console.error(err);
      error = 'Failed to save threat catalog item';
      showNotification('Failed to save threat catalog item', 'error');
    } finally {
      submitting = false;
    }
  }
  
  // Cancel form
  function handleCancel() {
    dispatch('cancel');
  }
  
  // Load threat data if in edit mode
  async function loadThreatData() {
    if (mode === 'edit' && threatId) {
      loading = true;
      error = '';
      
      try {
        const threat = await getThreatCatalogItem(threatId);
        if (threat) {
          title = threat.title;
          description = threat.description;
          strideCategory = threat.stride_category;
          componentTypes = threat.applicable_component_types;
          trustZones = threat.applicable_trust_zones;
          attackVectors = threat.attack_vectors;
          prerequisites = arrayToString(threat.prerequisites || []);
          typicalLikelihood = threat.typical_likelihood;
          typicalSeverity = threat.typical_severity;
          mitigationStrategies = threat.mitigation_strategies.length 
            ? threat.mitigation_strategies 
            : [createEmptyMitigationStrategy()];
          cweIds = arrayToString(threat.cwe_ids || []);
          capecIds = arrayToString(threat.capec_ids || []);
          examples = arrayToString(threat.examples || []);
        }
      } catch (err) {
        console.error(err);
        error = 'Failed to load threat data';
        showNotification('Failed to load threat data', 'error');
      } finally {
        loading = false;
      }
    }
  }
  
  onMount(() => {
    loadThreatData();
  });
</script>

<div class="p-4">
  {#if loading}
    <div class="flex justify-center py-8">
      <Spinner size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {error}</span>
    </div>
  {:else}
    <form on:submit|preventDefault={handleSubmit} class="space-y-6">
      <!-- Basic Information -->
      <div>
        <h3 class="text-lg font-medium mb-4">Basic Information</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="title" class="block text-sm font-medium">Title <span class="text-red-500">*</span></label>
            <input 
              id="title" 
              bind:value={title} 
              type="text" 
              class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
              required
            />
          </div>
          
          <div>
            <label for="strideCategory" class="block text-sm font-medium">STRIDE Category <span class="text-red-500">*</span></label>
            <select 
              id="strideCategory" 
              bind:value={strideCategory} 
              class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
            >
              {#each Object.entries(StrideCategory) as [key, value]}
                <option value={value}>{key.charAt(0) + key.slice(1).toLowerCase().replace('_', ' ')}</option>
              {/each}
            </select>
          </div>
        </div>
        
        <div class="mt-3">
          <label for="description" class="block text-sm font-medium">Description <span class="text-red-500">*</span></label>
          <textarea 
            id="description" 
            bind:value={description} 
            rows="3" 
            class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
            required
          ></textarea>
        </div>
      </div>
      
      <!-- Applicability -->
      <div>
        <h3 class="text-lg font-medium mb-4">Applicability</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium">Component Types</label>
            <div class="mt-1 border border-gray-300 rounded-md p-2 h-32 overflow-y-auto">
              {#each Object.entries(ComponentType) as [key, value]}
                <label class="flex items-center space-x-2 p-1">
                  <input 
                    type="checkbox" 
                    value={value} 
                    checked={componentTypes.includes(value)}
                    on:change={(e) => {
                      if (e.target.checked) {
                        componentTypes = [...componentTypes, value];
                      } else {
                        componentTypes = componentTypes.filter(t => t !== value);
                      }
                    }}
                  />
                  <span>{key.charAt(0) + key.slice(1).toLowerCase().replace('_', ' ')}</span>
                </label>
              {/each}
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium">Trust Zones</label>
            <div class="mt-1 border border-gray-300 rounded-md p-2 h-32 overflow-y-auto">
              {#each Object.entries(TrustZone) as [key, value]}
                <label class="flex items-center space-x-2 p-1">
                  <input 
                    type="checkbox" 
                    value={value} 
                    checked={trustZones.includes(value)}
                    on:change={(e) => {
                      if (e.target.checked) {
                        trustZones = [...trustZones, value];
                      } else {
                        trustZones = trustZones.filter(t => t !== value);
                      }
                    }}
                  />
                  <span>{key.charAt(0) + key.slice(1).toLowerCase()}</span>
                </label>
              {/each}
            </div>
          </div>
        </div>
        
        <div class="mt-3">
          <label class="block text-sm font-medium">Attack Vectors</label>
          <div class="mt-1 border border-gray-300 rounded-md p-2 grid grid-cols-2 md:grid-cols-3 gap-2 h-32 overflow-y-auto">
            {#each Object.entries(AttackVector) as [key, value]}
              <label class="flex items-center space-x-2 p-1">
                <input 
                  type="checkbox" 
                  value={value} 
                  checked={attackVectors.includes(value)}
                  on:change={(e) => {
                    if (e.target.checked) {
                      attackVectors = [...attackVectors, value];
                    } else {
                      attackVectors = attackVectors.filter(t => t !== value);
                    }
                  }}
                />
                <span>{key.charAt(0) + key.slice(1).toLowerCase().replace('_', ' ')}</span>
              </label>
            {/each}
          </div>
        </div>
      </div>
      
      <!-- Risk Assessment -->
      <div>
        <h3 class="text-lg font-medium mb-4">Risk Assessment</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="typicalLikelihood" class="block text-sm font-medium">Typical Likelihood (1-5)</label>
            <div class="flex items-center space-x-2 mt-1">
              <input 
                id="typicalLikelihood" 
                bind:value={typicalLikelihood} 
                type="range" 
                min="1" 
                max="5" 
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span class="text-lg font-semibold">{typicalLikelihood}</span>
            </div>
          </div>
          
          <div>
            <label for="typicalSeverity" class="block text-sm font-medium">Typical Severity (1-5)</label>
            <div class="flex items-center space-x-2 mt-1">
              <input 
                id="typicalSeverity" 
                bind:value={typicalSeverity} 
                type="range" 
                min="1" 
                max="5" 
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span class="text-lg font-semibold">{typicalSeverity}</span>
            </div>
          </div>
        </div>
        
        <div class="mt-3">
          <label for="prerequisites" class="block text-sm font-medium">Prerequisites (comma-separated)</label>
          <input 
            id="prerequisites" 
            bind:value={prerequisites} 
            type="text" 
            class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
            placeholder="E.g., Physical access, Network connectivity"
          />
        </div>
      </div>
      
      <!-- Mitigation Strategies -->
      <div>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium">Mitigation Strategies</h3>
          <button 
            type="button"
            on:click={addMitigationStrategy}
            class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 3a1 1 0 00-1 1v5H4a1 1 0 100 2h5v5a1 1 0 102 0v-5h5a1 1 0 100-2h-5V4a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            Add Strategy
          </button>
        </div>
        
        {#each mitigationStrategies as strategy, index}
          <div class="border rounded-md p-4 mb-4 bg-gray-50 relative">
            {#if mitigationStrategies.length > 1}
              <button 
                type="button"
                on:click={() => removeMitigationStrategy(index)}
                class="absolute top-2 right-2 text-red-600 hover:text-red-800"
                aria-label="Remove strategy"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            {/if}
            
            <div class="grid grid-cols-1 gap-4">
              <div>
                <label class="block text-sm font-medium">Title</label>
                <input 
                  bind:value={strategy.title} 
                  type="text" 
                  class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
                  placeholder="E.g., Implement secure authentication"
                  on:change={() => updateMitigationStrategy(index, 'title', strategy.title)}
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium">Description</label>
                <textarea 
                  bind:value={strategy.description} 
                  rows="2" 
                  class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
                  placeholder="Describe the mitigation strategy..."
                  on:change={() => updateMitigationStrategy(index, 'description', strategy.description)}
                ></textarea>
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium">Effectiveness (1-5)</label>
                  <div class="flex items-center space-x-2 mt-1">
                    <input 
                      bind:value={strategy.effectiveness} 
                      type="range" 
                      min="1" 
                      max="5" 
                      class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      on:change={() => updateMitigationStrategy(index, 'effectiveness', strategy.effectiveness)}
                    />
                    <span class="text-lg font-semibold">{strategy.effectiveness}</span>
                  </div>
                </div>
                
                <div>
                  <label class="block text-sm font-medium">Implementation Complexity (1-5)</label>
                  <div class="flex items-center space-x-2 mt-1">
                    <input 
                      bind:value={strategy.implementation_complexity} 
                      type="range" 
                      min="1" 
                      max="5" 
                      class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      on:change={() => updateMitigationStrategy(index, 'implementation_complexity', strategy.implementation_complexity)}
                    />
                    <span class="text-lg font-semibold">{strategy.implementation_complexity}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium">References (comma-separated)</label>
                <input 
                  type="text" 
                  class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
                  placeholder="E.g., NIST SP 800-63B, ISO 21434"
                  value={arrayToString(strategy.references || [])}
                  on:change={(e) => updateReferences(index, e.target.value)}
                />
              </div>
            </div>
          </div>
        {/each}
      </div>
      
      <!-- Additional Information -->
      <div>
        <h3 class="text-lg font-medium mb-4">Additional Information</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="cweIds" class="block text-sm font-medium">CWE IDs (comma-separated)</label>
            <input 
              id="cweIds" 
              bind:value={cweIds} 
              type="text" 
              class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
              placeholder="E.g., CWE-287, CWE-306"
            />
          </div>
          
          <div>
            <label for="capecIds" class="block text-sm font-medium">CAPEC IDs (comma-separated)</label>
            <input 
              id="capecIds" 
              bind:value={capecIds} 
              type="text" 
              class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
              placeholder="E.g., CAPEC-115, CAPEC-94"
            />
          </div>
        </div>
        
        <div class="mt-3">
          <label for="examples" class="block text-sm font-medium">Examples (comma-separated)</label>
          <input 
            id="examples" 
            bind:value={examples} 
            type="text" 
            class="mt-1 block w-full rounded-md border border-gray-300 shadow-sm p-2"
            placeholder="E.g., Smart home unauthorized access, Vehicle remote compromise"
          />
        </div>
      </div>
      
      <!-- Form Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t">
        <button 
          type="button"
          on:click={handleCancel}
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md"
          disabled={submitting}
        >
          Cancel
        </button>
        <button 
          type="submit"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center"
          disabled={submitting}
        >
          {#if submitting}
            <Spinner size="sm" class="mr-2" />
            Saving...
          {:else}
            {mode === 'create' ? 'Create' : 'Update'} Threat
          {/if}
        </button>
      </div>
    </form>
  {/if}
</div>
