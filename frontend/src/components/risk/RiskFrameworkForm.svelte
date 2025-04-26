<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createRiskFramework, updateRiskFramework, type RiskFramework, type RiskFrameworkCreate, type RiskFrameworkUpdate } from '../../api/risk';
  import RiskMatrixVisualization from './RiskMatrixVisualization.svelte';
  
  // Props
  export let framework: RiskFramework | null = null;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Form state
  let name = framework?.name || '';
  let description = framework?.description || '';
  
  // Version handling - not directly editable for existing frameworks
  let version = framework?.version || '1.0.0';
  let isNewFramework = !framework;
  
  // Determine if this is a minor or major update
  let updateType: 'minor' | 'major' = 'minor';
  
  // Simplified initial data for new framework
  const defaultImpactDefinitions: Record<string, Array<{
    category: 'safety' | 'financial' | 'operational' | 'privacy' | 'reputation' | 'compliance';
    level: 'negligible' | 'minor' | 'moderate' | 'major' | 'critical';
    description: string;
    numerical_value: number;
    examples: string[];
  }>> = {
    safety: [
      {
        category: 'safety',
        level: 'negligible',
        description: 'No injuries or safety impact',
        numerical_value: 1,
        examples: ['No safety impact']
      },
      {
        category: 'safety',
        level: 'minor',
        description: 'Minor injuries possible',
        numerical_value: 2,
        examples: ['Minor discomfort']
      },
      {
        category: 'safety',
        level: 'moderate',
        description: 'Injuries requiring medical attention',
        numerical_value: 3,
        examples: ['Hospitalization may be required']
      },
      {
        category: 'safety',
        level: 'major',
        description: 'Severe injuries likely',
        numerical_value: 4,
        examples: ['Extended hospital stay required']
      },
      {
        category: 'safety',
        level: 'critical',
        description: 'Life-threatening or fatal injuries',
        numerical_value: 5,
        examples: ['Death or permanent disability']
      }
    ],
    financial: [
      {
        category: 'financial',
        level: 'negligible',
        description: 'Minimal financial impact',
        numerical_value: 1,
        examples: ['Less than $10,000']
      },
      {
        category: 'financial',
        level: 'critical',
        description: 'Severe financial impact',
        numerical_value: 5,
        examples: ['Greater than $10,000,000']
      }
    ]
  };
  
  const defaultLikelihoodDefinitions: Array<{
    level: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost_certain';
    description: string;
    numerical_value: number;
    probability_range?: { min: number; max: number };
    examples: string[];
  }> = [
    {
      level: 'rare',
      description: 'Very unlikely to occur',
      numerical_value: 1,
      examples: ['Highly sophisticated attack requiring nation-state resources']
    },
    {
      level: 'unlikely',
      description: 'Not likely to occur',
      numerical_value: 2,
      examples: ['Advanced technical skills required']
    },
    {
      level: 'possible',
      description: 'May occur occasionally',
      numerical_value: 3,
      examples: ['Moderate technical skills required']
    },
    {
      level: 'likely',
      description: 'Likely to occur',
      numerical_value: 4,
      examples: ['Basic technical skills sufficient']
    },
    {
      level: 'almost_certain',
      description: 'Almost certain to occur',
      numerical_value: 5,
      examples: ['Trivial attack, script kiddie level']
    }
  ];
  
  // Generate a standard 5x5 risk matrix
  function generateStandardRiskMatrix() {
    const matrix: Array<{
      impact: number;
      likelihood: number;
      risk_level: 'low' | 'medium' | 'high' | 'critical';
      numerical_score: number;
    }> = [];
    
    for (let impact = 1; impact <= 5; impact++) {
      for (let likelihood = 1; likelihood <= 5; likelihood++) {
        const score = impact * likelihood;
        let risk_level: 'low' | 'medium' | 'high' | 'critical' = 'low';
        
        if (score >= 15) {
          risk_level = 'critical';
        } else if (score >= 10) {
          risk_level = 'high';
        } else if (score >= 5) {
          risk_level = 'medium';
        }
        
        matrix.push({
          impact,
          likelihood,
          risk_level,
          numerical_score: score
        });
      }
    }
    
    return {
      matrix,
      description: 'Standard 5x5 Risk Matrix'
    };
  }
  
  const defaultRiskThresholds: Array<{
    level: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    requires_approval: boolean;
    approvers: string[];
    max_acceptable_score: number;
  }> = [
    {
      level: 'low',
      description: 'Acceptable risk',
      requires_approval: false,
      approvers: [],
      max_acceptable_score: 4
    },
    {
      level: 'medium',
      description: 'Needs review',
      requires_approval: true,
      approvers: ['Security Analyst'],
      max_acceptable_score: 9
    },
    {
      level: 'high',
      description: 'Requires mitigation',
      requires_approval: true,
      approvers: ['Security Analyst', 'Security Manager'],
      max_acceptable_score: 16
    },
    {
      level: 'critical',
      description: 'Unacceptable risk',
      requires_approval: true,
      approvers: ['Security Analyst', 'Security Manager', 'CISO'],
      max_acceptable_score: 25
    }
  ];
  
  // Form data
  let impactDefinitions = framework?.impact_definitions || defaultImpactDefinitions;
  let likelihoodDefinitions = framework?.likelihood_definitions || defaultLikelihoodDefinitions;
  let riskMatrix = framework?.risk_matrix || generateStandardRiskMatrix();
  let riskThresholds = framework?.risk_thresholds || defaultRiskThresholds;
  
  // Form validation and submission state
  let isSubmitting = false;
  let error = '';
  let currentTab = 'basic'; // basic, impact, likelihood, matrix, thresholds
  
  // Form validation
  function validateForm() {
    if (!name.trim()) {
      error = 'Framework name is required';
      return false;
    }
    
    if (!version.trim()) {
      error = 'Version is required';
      return false;
    }
    
    return true;
  }
  
  // Create a new version number
  function incrementVersion(currentVersion: string, isMajorUpdate: boolean): string {
    const parts = currentVersion.split('.');
    if (parts.length !== 3) return '1.0.0'; // Invalid format, reset to 1.0.0
    
    if (isMajorUpdate) {
      // Major update: increment first number, reset others to 0
      return `${parseInt(parts[0]) + 1}.0.0`;
    } else {
      // Minor update: increment second number, reset third to 0
      return `${parts[0]}.${parseInt(parts[1]) + 1}.0`;
    }
  }
  
  // Submit form
  async function handleSubmit() {
    if (!validateForm()) return;
    
    isSubmitting = true;
    error = '';
    
    try {
      if (framework) {
        // Update existing framework - calculate new version based on update type
        const newVersion = incrementVersion(framework.version, updateType === 'major');
        
        const updateData: RiskFrameworkUpdate = {
          name,
          description,
          version: newVersion,
          impact_definitions: impactDefinitions,
          likelihood_definitions: likelihoodDefinitions,
          risk_matrix: riskMatrix,
          risk_thresholds: riskThresholds
        };
        
        await updateRiskFramework(framework.framework_id, updateData);
      } else {
        // Create new framework
        const newFramework: RiskFrameworkCreate = {
          name,
          description,
          version,
          impact_definitions: impactDefinitions,
          likelihood_definitions: likelihoodDefinitions,
          risk_matrix: riskMatrix,
          risk_thresholds: riskThresholds
        };
        
        await createRiskFramework(newFramework);
      }
      
      dispatch('complete', { success: true });
    } catch (e: any) {
      error = e.message || 'Failed to save risk framework';
      console.error('Error saving risk framework:', e);
    } finally {
      isSubmitting = false;
    }
  }
  
  function cancelForm() {
    dispatch('complete', { success: false });
  }
</script>

<div class="risk-framework-form">
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <p>{error}</p>
    </div>
  {/if}
  
  <!-- Tab navigation -->
  <div class="mb-6 border-b" style="border-color: var(--color-border);">
    <nav class="flex">
      <button 
        class="py-2 px-4 text-center {currentTab === 'basic' ? 'border-b-2 font-medium' : ''}" 
        style="border-color: var(--color-primary);"
        on:click={() => currentTab = 'basic'}
      >
        Basic Info
      </button>
      <button 
        class="py-2 px-4 text-center {currentTab === 'matrix' ? 'border-b-2 font-medium' : ''}" 
        style="border-color: var(--color-primary);"
        on:click={() => currentTab = 'matrix'}
      >
        Risk Matrix
      </button>
      <button 
        class="py-2 px-4 text-center {currentTab === 'impact' ? 'border-b-2 font-medium' : ''}" 
        style="border-color: var(--color-primary);"
        on:click={() => currentTab = 'impact'}
      >
        Impact Definitions
      </button>
      <button 
        class="py-2 px-4 text-center {currentTab === 'likelihood' ? 'border-b-2 font-medium' : ''}" 
        style="border-color: var(--color-primary);"
        on:click={() => currentTab = 'likelihood'}
      >
        Likelihood
      </button>
      <button 
        class="py-2 px-4 text-center {currentTab === 'thresholds' ? 'border-b-2 font-medium' : ''}" 
        style="border-color: var(--color-primary);"
        on:click={() => currentTab = 'thresholds'}
      >
        Thresholds
      </button>
    </nav>
  </div>
  
  <!-- Content based on active tab -->
  <div>
    {#if currentTab === 'basic'}
      <div class="space-y-4">
        <div>
          <label for="name" class="block text-sm font-medium mb-1">Framework Name*</label>
          <input 
            type="text" 
            id="name" 
            bind:value={name}
            class="w-full px-3 py-2 border rounded-md"
            style="border-color: var(--color-border);"
            placeholder="Automotive TARA Framework"
            required
          />
        </div>
        
        <div>
          <label for="description" class="block text-sm font-medium mb-1">Description</label>
          <textarea 
            id="description" 
            bind:value={description}
            class="w-full px-3 py-2 border rounded-md"
            style="border-color: var(--color-border);"
            placeholder="Framework description..."
            rows="3"
          ></textarea>
        </div>
        
        <div>
          {#if isNewFramework}
            <!-- Version field for new frameworks -->
            <label for="version" class="block text-sm font-medium mb-1">Version*</label>
            <input 
              type="text" 
              id="version" 
              bind:value={version}
              class="w-full px-3 py-2 border rounded-md"
              style="border-color: var(--color-border);"
              placeholder="1.0.0"
              required
            />
          {:else}
            <!-- Version update option for existing frameworks -->
            <p class="block text-sm font-medium mb-1">Version Update</p>
            <div class="mb-4">
              <p class="text-sm text-gray-600 mb-2">Current version: <span class="font-bold">{framework?.version}</span></p>
              <p class="text-sm text-gray-600 mb-2">Select update type:</p>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="radio" bind:group={updateType} value="minor" class="mr-2" />
                  <span>Minor update ({incrementVersion(framework?.version || '1.0.0', false)})</span>
                </label>
                <label class="flex items-center">
                  <input type="radio" bind:group={updateType} value="major" class="mr-2" />
                  <span>Major update ({incrementVersion(framework?.version || '1.0.0', true)})</span>
                </label>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {:else if currentTab === 'matrix'}
      <div>
        <h3 class="text-lg font-medium mb-4">Risk Matrix</h3>
        <p class="mb-4 text-sm">The risk matrix defines how impact and likelihood values combine to determine risk levels.</p>
        
        <div class="mb-6">
          <RiskMatrixVisualization 
            riskMatrix={riskMatrix} 
            title="Current Risk Matrix"
          />
        </div>
        
        <p class="mt-4 text-sm text-gray-600">
          <strong>Note:</strong> This preview version uses a standard 5x5 risk matrix. In the future, you'll be able to customize each cell.
        </p>
      </div>
    {:else if currentTab === 'impact'}
      <div>
        <h3 class="text-lg font-medium mb-4">Impact Definitions</h3>
        <p class="mb-4 text-sm">Define the impact categories and their severity levels used in the risk matrix.</p>
        
        <!-- Impact Categories -->
        <div class="mb-6">
          <h4 class="text-md font-medium mb-3">Impact Categories</h4>
          
          <div class="mb-4 flex justify-end">
            <div class="dropdown relative">
              <button 
                class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors inline-flex items-center"
                type="button"
                on:click={() => {
                  // Add a new impact category
                  const newCategory = prompt('Enter new impact category name (e.g., operational, privacy, reputation, compliance)');
                  if (newCategory && newCategory.trim()) {
                    const categoryKey = newCategory.trim().toLowerCase();
                    if (!impactDefinitions[categoryKey]) {
                      impactDefinitions[categoryKey] = [{
                        category: categoryKey,
                        level: 'moderate',
                        description: `New ${categoryKey} impact level`,
                        numerical_value: 3,
                        examples: ['Example impact']
                      }];
                      impactDefinitions = {...impactDefinitions};
                    }
                  }
                }}
              >
                Add New Impact Category
              </button>
            </div>
          </div>
          
          <!-- Safety Impact Category -->
          <div class="mb-6 p-4 border rounded-md" style="border-color: var(--color-border);">
            <h5 class="font-medium mb-2">Safety Impact</h5>
            <p class="text-sm text-gray-600 mb-3">Impacts related to human safety and health.</p>
            
            <div class="overflow-x-auto">
              <table class="min-w-full border-collapse">
                <thead>
                  <tr>
                    <th class="border p-2 bg-gray-100 text-left">Level</th>
                    <th class="border p-2 bg-gray-100 text-left">Description</th>
                    <th class="border p-2 bg-gray-100 text-left">Value</th>
                    <th class="border p-2 bg-gray-100 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {#each impactDefinitions['safety'] || [] as def, index}
                    <tr>
                      <td class="border p-2">
                        <select 
                          bind:value={def.level} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        >
                          <option value="negligible">Negligible</option>
                          <option value="minor">Minor</option>
                          <option value="moderate">Moderate</option>
                          <option value="major">Major</option>
                          <option value="critical">Critical</option>
                        </select>
                      </td>
                      <td class="border p-2">
                        <input 
                          type="text" 
                          bind:value={def.description} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        />
                      </td>
                      <td class="border p-2">
                        <input 
                          type="number" 
                          min="1" 
                          max="5" 
                          bind:value={def.numerical_value} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        />
                      </td>
                      <td class="border p-2 text-center">
                        <button 
                          class="text-red-600 hover:text-red-800"
                          title="Remove level"
                          on:click={() => {
                            if (impactDefinitions['safety'].length > 1) {
                              impactDefinitions['safety'].splice(index, 1);
                              impactDefinitions = {...impactDefinitions};
                            }
                          }}
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
            
            <button 
              class="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              on:click={() => {
                if (!impactDefinitions['safety']) impactDefinitions['safety'] = [];
                impactDefinitions['safety'].push({
                  category: 'safety',
                  level: 'minor',
                  description: 'New safety impact level',
                  numerical_value: 2,
                  examples: ['Example impact']
                });
                impactDefinitions = {...impactDefinitions};
              }}
            >
              Add Safety Level
            </button>
          </div>
          
          <!-- Financial Impact Category -->
          <div class="mb-6 p-4 border rounded-md" style="border-color: var(--color-border);">
            <h5 class="font-medium mb-2">Financial Impact</h5>
            <p class="text-sm text-gray-600 mb-3">Impacts related to financial loss or damage.</p>
            
            <div class="overflow-x-auto">
              <table class="min-w-full border-collapse">
                <thead>
                  <tr>
                    <th class="border p-2 bg-gray-100 text-left">Level</th>
                    <th class="border p-2 bg-gray-100 text-left">Description</th>
                    <th class="border p-2 bg-gray-100 text-left">Value</th>
                    <th class="border p-2 bg-gray-100 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {#each impactDefinitions['financial'] || [] as def, index}
                    <tr>
                      <td class="border p-2">
                        <select 
                          bind:value={def.level} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        >
                          <option value="negligible">Negligible</option>
                          <option value="minor">Minor</option>
                          <option value="moderate">Moderate</option>
                          <option value="major">Major</option>
                          <option value="critical">Critical</option>
                        </select>
                      </td>
                      <td class="border p-2">
                        <input 
                          type="text" 
                          bind:value={def.description} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        />
                      </td>
                      <td class="border p-2">
                        <input 
                          type="number" 
                          min="1" 
                          max="5" 
                          bind:value={def.numerical_value} 
                          class="w-full p-1 border rounded"
                          style="border-color: var(--color-border);"
                        />
                      </td>
                      <td class="border p-2 text-center">
                        <button 
                          class="text-red-600 hover:text-red-800"
                          title="Remove level"
                          on:click={() => {
                            if (impactDefinitions['financial'].length > 1) {
                              impactDefinitions['financial'].splice(index, 1);
                              impactDefinitions = {...impactDefinitions};
                            }
                          }}
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
              
              <button 
                class="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                on:click={() => {
                  if (!impactDefinitions['financial']) impactDefinitions['financial'] = [];
                  impactDefinitions['financial'].push({
                    category: 'financial',
                    level: 'minor',
                    description: 'Financial impact',
                    numerical_value: 2,
                    examples: ['Example']
                  });
                  impactDefinitions = {...impactDefinitions};
                }}
              >
                Add Level
              </button>
            </div>
          </div>
          
          <!-- Render any additional impact categories dynamically -->
          {#each Object.entries(impactDefinitions).filter(([category]) => !['safety', 'financial'].includes(category)) as [category, definitions]}
            <div class="mb-6 p-4 border rounded-md" style="border-color: var(--color-border);">
              <div class="flex justify-between items-start">
                <div>
                  <h5 class="font-medium mb-2 capitalize">{category} Impact</h5>
                  <p class="text-sm text-gray-600 mb-3">Impacts related to {category}.</p>
                </div>
                <button 
                  class="text-red-600 hover:text-red-800 text-sm"
                  title="Remove category"
                  on:click={() => {
                    if (confirm(`Are you sure you want to remove the ${category} impact category?`)) {
                      const { [category]: removed, ...rest } = impactDefinitions;
                      impactDefinitions = rest;
                    }
                  }}
                >
                  Remove Category
                </button>
              </div>
              
              <div class="overflow-x-auto">
                <table class="min-w-full border-collapse">
                  <thead>
                    <tr>
                      <th class="border p-2 bg-gray-100 text-left">Level</th>
                      <th class="border p-2 bg-gray-100 text-left">Description</th>
                      <th class="border p-2 bg-gray-100 text-left">Value</th>
                      <th class="border p-2 bg-gray-100 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each definitions as def, index}
                      <tr>
                        <td class="border p-2">
                          <select 
                            bind:value={def.level} 
                            class="w-full p-1 border rounded"
                            style="border-color: var(--color-border);"
                          >
                            <option value="negligible">Negligible</option>
                            <option value="minor">Minor</option>
                            <option value="moderate">Moderate</option>
                            <option value="major">Major</option>
                            <option value="critical">Critical</option>
                          </select>
                        </td>
                        <td class="border p-2">
                          <input 
                            type="text" 
                            bind:value={def.description} 
                            class="w-full p-1 border rounded"
                            style="border-color: var(--color-border);"
                          />
                        </td>
                        <td class="border p-2">
                          <input 
                            type="number" 
                            min="1" 
                            max="5" 
                            bind:value={def.numerical_value} 
                            class="w-full p-1 border rounded"
                            style="border-color: var(--color-border);"
                          />
                        </td>
                        <td class="border p-2 text-center">
                          <button 
                            class="text-red-600 hover:text-red-800"
                            title="Remove level"
                            on:click={() => {
                              if (impactDefinitions[category].length > 1) {
                                impactDefinitions[category].splice(index, 1);
                                impactDefinitions = {...impactDefinitions};
                              }
                            }}
                          >
                            ✕
                          </button>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
                
                <button 
                  class="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  on:click={() => {
                    if (!impactDefinitions[category]) impactDefinitions[category] = [];
                    impactDefinitions[category].push({
                      category,
                      level: 'minor',
                      description: `${category} impact`,
                      numerical_value: 2,
                      examples: ['Example']
                    });
                    impactDefinitions = {...impactDefinitions};
                  }}
                >
                  Add Level
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {:else if currentTab === 'likelihood'}
      <div>
        <h3 class="text-lg font-medium mb-4">Likelihood Definitions</h3>
        <p class="mb-4 text-sm">Define the likelihood levels used in the risk matrix.</p>
        
        <div class="overflow-x-auto">
          <table class="min-w-full border-collapse">
            <thead>
              <tr>
                <th class="border p-2 bg-gray-100 text-left">Level</th>
                <th class="border p-2 bg-gray-100 text-left">Description</th>
                <th class="border p-2 bg-gray-100 text-left">Value</th>
                <th class="border p-2 bg-gray-100 text-left">Example</th>
                <th class="border p-2 bg-gray-100 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each likelihoodDefinitions as def, index}
                <tr>
                  <td class="border p-2">
                    <select 
                      bind:value={def.level} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    >
                      <option value="rare">Rare</option>
                      <option value="unlikely">Unlikely</option>
                      <option value="possible">Possible</option>
                      <option value="likely">Likely</option>
                      <option value="almost_certain">Almost Certain</option>
                    </select>
                  </td>
                  <td class="border p-2">
                    <input 
                      type="text" 
                      bind:value={def.description} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    />
                  </td>
                  <td class="border p-2">
                    <input 
                      type="number" 
                      min="1" 
                      max="5" 
                      bind:value={def.numerical_value} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    />
                  </td>
                  <td class="border p-2">
                    <input 
                      type="text" 
                      bind:value={def.examples[0]} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    />
                  </td>
                  <td class="border p-2 text-center">
                    <button 
                      class="text-red-600 hover:text-red-800"
                      title="Remove level"
                      on:click={() => {
                        if (likelihoodDefinitions.length > 1) {
                          likelihoodDefinitions.splice(index, 1);
                          likelihoodDefinitions = [...likelihoodDefinitions];
                        }
                      }}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          
          <button 
            class="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            on:click={() => {
              likelihoodDefinitions.push({
                level: 'possible',
                description: 'New likelihood level',
                numerical_value: 3,
                examples: ['Example description']
              });
              likelihoodDefinitions = [...likelihoodDefinitions];
            }}
          >
            Add Likelihood Level
          </button>
        </div>
      </div>
    {:else if currentTab === 'thresholds'}
      <div>
        <h3 class="text-lg font-medium mb-4">Risk Thresholds</h3>
        <p class="mb-4 text-sm">Define the thresholds for different risk levels and approval requirements.</p>
        
        <div class="overflow-x-auto">
          <table class="min-w-full border-collapse">
            <thead>
              <tr>
                <th class="border p-2 bg-gray-100 text-left">Risk Level</th>
                <th class="border p-2 bg-gray-100 text-left">Description</th>
                <th class="border p-2 bg-gray-100 text-left">Max Score</th>
                <th class="border p-2 bg-gray-100 text-left">Requires Approval</th>
                <th class="border p-2 bg-gray-100 text-left">Approvers</th>
                <th class="border p-2 bg-gray-100 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each riskThresholds as threshold, index}
                <tr>
                  <td class="border p-2">
                    <select 
                      bind:value={threshold.level} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </td>
                  <td class="border p-2">
                    <input 
                      type="text" 
                      bind:value={threshold.description} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    />
                  </td>
                  <td class="border p-2">
                    <input 
                      type="number" 
                      min="1" 
                      max="25" 
                      bind:value={threshold.max_acceptable_score} 
                      class="w-full p-1 border rounded"
                      style="border-color: var(--color-border);"
                    />
                  </td>
                  <td class="border p-2 text-center">
                    <input 
                      type="checkbox" 
                      bind:checked={threshold.requires_approval} 
                    />
                  </td>
                  <td class="border p-2">
                    <input 
                      type="text" 
                      bind:value={threshold.approvers[0]} 
                      class="w-full p-1 border rounded mb-1"
                      style="border-color: var(--color-border);"
                      placeholder="Primary approver"
                    />
                    {#if threshold.approvers.length > 1}
                      <input 
                        type="text" 
                        bind:value={threshold.approvers[1]} 
                        class="w-full p-1 border rounded"
                        style="border-color: var(--color-border);"
                        placeholder="Secondary approver"
                      />
                    {/if}
                  </td>
                  <td class="border p-2 text-center">
                    <button 
                      class="text-red-600 hover:text-red-800"
                      title="Remove threshold"
                      on:click={() => {
                        if (riskThresholds.length > 1) {
                          riskThresholds.splice(index, 1);
                          riskThresholds = [...riskThresholds];
                        }
                      }}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          
          <button 
            class="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            on:click={() => {
              riskThresholds.push({
                level: 'medium',
                description: 'New threshold level',
                requires_approval: true,
                approvers: ['Approver name'],
                max_acceptable_score: 10
              });
              riskThresholds = [...riskThresholds];
            }}
          >
            Add Threshold
          </button>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Form buttons -->
  <div class="flex justify-end space-x-3 mt-8">
    <button 
      type="button" 
      class="px-4 py-2 border rounded-md" 
      style="border-color: var(--color-border);"
      on:click={cancelForm}
      disabled={isSubmitting}
    >
      Cancel
    </button>
    <button 
      type="button" 
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      on:click={handleSubmit}
      disabled={isSubmitting}
    >
      {isSubmitting ? 'Saving...' : (framework ? 'Update' : 'Create')}
    </button>
  </div>
</div>
