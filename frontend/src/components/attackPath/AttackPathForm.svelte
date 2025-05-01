<!-- Attack Path Analysis Form Component -->
<script>
  import { onMount } from 'svelte';
  import {
    generateAttackPaths,
    AttackPathRequest,
    AttackPathAssumption,
    AttackPathConstraint,
    ThreatScenario
  } from '../../api/attackPath';
  import { getComponents } from '../../api/component';
  import { getVulnerabilities } from '../../api/vulnerability';
  import Loading from '../common/Loading.svelte';
  import Dropdown from '../common/Dropdown.svelte';
  import MultiSelect from '../common/MultiSelect.svelte';
  import Alert from '../common/Alert.svelte';
  
  // Form state
  let loading = false;
  let error = null;
  let success = null;
  
  // Data for form
  let components = [];
  let selectedComponentId = '';
  let selectedComponents = [];
  let entryPoints = [];
  let targets = [];
  let vulnerabilities = [];
  let selectedVulnerabilities = [];
  
  // Analysis settings
  let includeChains = true;
  let maxDepth = 5;
  
  // Assumptions, Constraints, and Threat Scenarios
  let assumptions = [];
  let constraints = [];
  let threatScenarios = [];
  
  // Predefined constraints
  const availableConstraints = [
    { 
      constraint_id: 'constraint_1', 
      description: 'Exclude physical access to microcontrollers', 
      type: 'exclude_physical_access' 
    },
    { 
      constraint_id: 'constraint_2', 
      description: 'Require local network access', 
      type: 'require_local_access' 
    },
    { 
      constraint_id: 'constraint_3', 
      description: 'Exclude component type: Sensor', 
      type: 'exclude_component_type' 
    }
  ];
  
  // Predefined assumption types
  const availableAssumptions = [
    { 
      assumption_id: 'assume_1', 
      description: 'Attacker has physical access', 
      type: 'physical_access' 
    },
    { 
      assumption_id: 'assume_2', 
      description: 'Attacker has local network access', 
      type: 'local_network_access' 
    },
    { 
      assumption_id: 'assume_3', 
      description: 'Attacker has sophisticated skills', 
      type: 'skilled_attacker' 
    }
  ];
  
  // Predefined threat scenarios (STRIDE+)
  const availableThreatScenarios = [
    {
      scenario_id: 'threat_s1',
      name: 'Authentication Bypass',
      description: 'Attacker bypasses authentication mechanisms',
      threat_type: 'spoofing',
      likelihood: 0.7
    },
    {
      scenario_id: 'threat_t1',
      name: 'Firmware Tampering',
      description: 'Attacker modifies firmware to alter component behavior',
      threat_type: 'tampering',
      likelihood: 0.6
    },
    {
      scenario_id: 'threat_r1',
      name: 'Unauthorized Data Access',
      description: 'Attacker accesses sensitive data without authorization',
      threat_type: 'information_disclosure',
      likelihood: 0.8
    },
    {
      scenario_id: 'threat_d1',
      name: 'DoS Attack',
      description: 'Attacker overloads system causing denial of service',
      threat_type: 'denial_of_service',
      likelihood: 0.5
    },
    {
      scenario_id: 'threat_e1',
      name: 'Privilege Escalation',
      description: 'Attacker gains higher privileges than authorized',
      threat_type: 'elevation_of_privilege',
      likelihood: 0.6
    }
  ];
  
  // Result of analysis
  let analysisResult = null;
  
  onMount(async () => {
    try {
      // Load components
      loading = true;
      const result = await getComponents();
      console.log('Component result from API:', result);
      
      if (result && result.components) {
        components = result.components || [];
        console.log('Components loaded:', components);
        
        // Debug the first component to verify properties
        if (components.length > 0) {
          console.log('First component:', components[0]);
          console.log('component_id property exists:', 'component_id' in components[0]);
          console.log('id property exists:', 'id' in components[0]);
        }
      } else {
        console.error('Invalid component data structure:', result);
        error = 'Failed to load components. Invalid data structure received.';
      }
      
      // Load vulnerabilities
      const vulnResult = await getVulnerabilities();
      vulnerabilities = vulnResult.vulnerabilities || [];
      
      loading = false;
    } catch (err) {
      console.error('Error loading data:', err);
      error = 'Failed to load components and vulnerabilities. Please try refreshing the page.';
      loading = false;
    }
  });
  
  function handleSelectComponent(event) {
    const componentId = event.target.value;
    selectedComponentId = componentId;
    
    // Add to selected components if not already there
    if (!selectedComponents.includes(componentId) && componentId) {
      selectedComponents = [...selectedComponents, componentId];
    }
  }
  
  function addSelectedComponent() {
    if (selectedComponentId && !selectedComponents.includes(selectedComponentId)) {
      selectedComponents = [...selectedComponents, selectedComponentId];
    }
  }
  
  function removeComponent(componentId) {
    selectedComponents = selectedComponents.filter(id => id !== componentId);
    
    // Also remove from entry points and targets
    entryPoints = entryPoints.filter(id => id !== componentId);
    targets = targets.filter(id => id !== componentId);
  }
  
  function toggleEntryPoint(componentId) {
    if (entryPoints.includes(componentId)) {
      entryPoints = entryPoints.filter(id => id !== componentId);
    } else {
      entryPoints = [...entryPoints, componentId];
    }
  }
  
  function toggleTarget(componentId) {
    if (targets.includes(componentId)) {
      targets = targets.filter(id => id !== componentId);
    } else {
      targets = [...targets, componentId];
    }
  }
  
  function toggleAssumption(assumption) {
    const exists = assumptions.find(a => a.assumption_id === assumption.assumption_id);
    if (exists) {
      assumptions = assumptions.filter(a => a.assumption_id !== assumption.assumption_id);
    } else {
      assumptions = [...assumptions, assumption];
    }
  }
  
  function toggleConstraint(constraint) {
    const exists = constraints.find(c => c.constraint_id === constraint.constraint_id);
    if (exists) {
      constraints = constraints.filter(c => c.constraint_id !== constraint.constraint_id);
    } else {
      constraints = [...constraints, constraint];
    }
  }
  
  function toggleThreatScenario(scenario) {
    const exists = threatScenarios.find(s => s.scenario_id === scenario.scenario_id);
    if (exists) {
      threatScenarios = threatScenarios.filter(s => s.scenario_id !== scenario.scenario_id);
    } else {
      threatScenarios = [...threatScenarios, scenario];
    }
  }
  
  function toggleVulnerability(vulnerabilityId) {
    if (selectedVulnerabilities.includes(vulnerabilityId)) {
      selectedVulnerabilities = selectedVulnerabilities.filter(id => id !== vulnerabilityId);
    } else {
      selectedVulnerabilities = [...selectedVulnerabilities, vulnerabilityId];
    }
  }
  
  async function generateAnalysis() {
    if (!selectedComponentId) {
      error = 'Please select a primary component for analysis';
      return;
    }
    
    if (selectedComponents.length === 0) {
      error = 'Please select at least one component to analyze';
      return;
    }
    
    // Check if we have target components selected
    if (targets.length === 0) {
      error = 'Please select at least one target component';
      return;
    }
    
    try {
      loading = true;
      error = null;
      success = null;
      
      // Ensure primary component is included in selected components
      if (!selectedComponents.includes(selectedComponentId)) {
        selectedComponents = [...selectedComponents, selectedComponentId];
      }
      
      // Get component types for validation
      const componentTypes = {};
      components.forEach(comp => {
        componentTypes[comp.component_id] = comp.type;
      });
      
      console.log('Component types for validation:', componentTypes);
      
      // Validate constraints against selected components
      const filteredConstraints = constraints.filter(constraint => {
        // Check if we're excluding component types that are needed for analysis
        if (constraint.type === 'exclude_component_type') {
          const excludedType = constraint.description.replace('Exclude component type: ', '');
          console.log(`Checking constraint for excluding ${excludedType}`);
          
          // Check if any selected component is of the excluded type
          const typesInSelection = new Set(
            selectedComponents.map(id => componentTypes[id])
          );
          console.log('Types in selection:', Array.from(typesInSelection));
          
          if (typesInSelection.size === 1 && typesInSelection.has(excludedType)) {
            console.log(`Warning: Removing constraint that would exclude all components (${excludedType})`);
            return false;
          }
        }
        return true;
      });
      
      if (filteredConstraints.length !== constraints.length) {
        console.log('Removed conflicting constraints that would exclude all components');
      }
      
      // Ensure proper entry/exit points
      // If a component is both an entry point and a target, it needs to be validated differently
      if (entryPoints.length === 1 && targets.length === 1 && entryPoints[0] === targets[0]) {
        // Same component as entry and target, ensure we have at least one more component for a valid path
        if (selectedComponents.length < 2) {
          error = 'When using the same component as entry point and target, you need at least one additional component';
          loading = false;
          return;
        }
      }
      
      // Build the request using the AttackPathRequest class
      const request = new AttackPathRequest({
        primary_component_id: selectedComponentId,
        component_ids: selectedComponents,
        entry_point_ids: entryPoints.length > 0 ? entryPoints : undefined,
        target_ids: targets,
        include_chains: includeChains,
        max_depth: maxDepth,
        assumptions: assumptions,
        constraints: filteredConstraints, // Use filtered constraints that won't cause conflicts
        threat_scenarios: threatScenarios,
        vulnerability_ids: selectedVulnerabilities
      });
      
      console.log('Sending attack path analysis request:', request);
      
      // Generate attack paths
      const result = await generateAttackPaths(request);
      analysisResult = result;
      success = 'Attack path analysis completed successfully!';
      console.log('Analysis result:', result);
      
    } catch (err) {
      console.error('Error generating attack paths:', err);
      error = `Failed to generate attack paths: ${err.message || 'Unknown error'}`;
    } finally {
      loading = false;
    }
  }
</script>

<div class="container mx-auto p-4">
  <h2 class="text-2xl font-bold mb-6">Attack Path Analysis</h2>
  
  {#if error}
    <Alert type="error" message={error} />
  {/if}
  
  {#if success}
    <Alert type="success" message={success} />
  {/if}

  <!-- Debug information (only visible during development) -->
  {#if components.length === 0 && !loading}
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-yellow-700">
            No components loaded. Please check the browser console for details.
          </p>
        </div>
      </div>
    </div>
  {/if}
  
  <div class="bg-white shadow rounded-lg p-6 mb-6">
    <h3 class="text-xl font-semibold mb-4">Analysis Configuration</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Primary Component Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Primary Component (Focal Point)
        </label>
        <select 
        class="w-full px-3 py-2 border border-gray-300 rounded-md"
        bind:value={selectedComponentId}
        on:change={handleSelectComponent}
        >
        <option value="">Select a component...</option>
        {#each components as component}
        <option value={component.component_id || component.id}>
            {component.name} ({component.component_id || component.id})
            </option>
            {/each}
          </select>
      </div>
      
      <!-- Analysis Settings -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Analysis Settings
        </label>
        <div class="flex items-center mb-2">
          <input 
            type="checkbox" 
            id="includeChains"
            bind:checked={includeChains}
            class="mr-2"
          />
          <label for="includeChains" class="text-sm">Include Attack Chains</label>
        </div>
        <div class="flex items-center">
          <label for="maxDepth" class="text-sm mr-2">Max Path Depth:</label>
          <input 
            type="number" 
            id="maxDepth"
            bind:value={maxDepth}
            min="1" 
            max="10"
            class="w-20 px-2 py-1 border border-gray-300 rounded-md"
          />
        </div>
      </div>
    </div>
    
    <!-- Selected Components -->
    <div class="mt-6">
      <h4 class="text-lg font-medium mb-2">Selected Components</h4>
      <div class="bg-gray-50 p-4 rounded-md">
        {#if selectedComponents.length === 0}
          <p class="text-gray-500 italic">No components selected</p>
        {:else}
          {#if targets.length === 0}
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-yellow-800">
                    You need to select at least one target component
                  </p>
                  <p class="text-sm text-yellow-700">
                    Click the "Target" button on one or more components below to set them as attack targets.
                  </p>
                </div>
              </div>
            </div>
          {/if}
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {#each selectedComponents as componentId}
              {@const component = components.find(c => (c.component_id || c.id) === componentId)}
              {#if component}
                <div class="flex items-center justify-between bg-white p-2 rounded border">
                  <div class="flex-grow mr-2">
                    <p class="font-medium">{component.name}</p>
                    <p class="text-xs text-gray-500">{component.component_id || component.id}</p>
                  </div>
                  <div class="flex space-x-1">
                    <button 
                      class="p-1 text-xs rounded {entryPoints.includes(componentId) ? 'bg-blue-500 text-white' : 'bg-gray-200'}"
                      on:click={() => toggleEntryPoint(componentId)}
                      title="Toggle as entry point"
                    >
                      Entry
                    </button>
                    <button 
                      class="p-1 text-xs rounded {targets.includes(componentId) ? 'bg-red-500 text-white' : 'bg-gray-200'}"
                      on:click={() => toggleTarget(componentId)}
                      title="Toggle as target"
                    >
                      Target
                    </button>
                    <button 
                      class="p-1 text-xs rounded bg-gray-200 hover:bg-gray-300"
                      on:click={() => removeComponent(componentId)}
                      title="Remove component"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              {/if}
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Assumptions, Constraints, and Threats -->
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Assumptions -->
      <div>
        <h4 class="text-lg font-medium mb-2">Assumptions</h4>
        <div class="bg-gray-50 p-3 rounded-md space-y-2">
          {#each availableAssumptions as assumption}
            <div class="flex items-center">
              <input 
                type="checkbox" 
                id={assumption.assumption_id}
                checked={assumptions.some(a => a.assumption_id === assumption.assumption_id)}
                on:change={() => toggleAssumption(assumption)}
                class="mr-2"
              />
              <label for={assumption.assumption_id} class="text-sm">
                {assumption.description}
              </label>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Constraints -->
      <div>
        <h4 class="text-lg font-medium mb-2">Constraints</h4>
        <div class="bg-gray-50 p-3 rounded-md space-y-2">
          {#each availableConstraints as constraint}
            <div class="flex items-center">
              <input 
                type="checkbox" 
                id={constraint.constraint_id}
                checked={constraints.some(c => c.constraint_id === constraint.constraint_id)}
                on:change={() => toggleConstraint(constraint)}
                class="mr-2"
              />
              <label for={constraint.constraint_id} class="text-sm">
                {constraint.description}
              </label>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Threat Scenarios -->
      <div>
        <h4 class="text-lg font-medium mb-2">Threat Scenarios</h4>
        <div class="bg-gray-50 p-3 rounded-md space-y-2">
          {#each availableThreatScenarios as scenario}
            <div class="flex items-center">
              <input 
                type="checkbox" 
                id={scenario.scenario_id}
                checked={threatScenarios.some(s => s.scenario_id === scenario.scenario_id)}
                on:change={() => toggleThreatScenario(scenario)}
                class="mr-2"
              />
              <label for={scenario.scenario_id} class="text-sm">
                {scenario.name} ({scenario.threat_type})
              </label>
            </div>
          {/each}
        </div>
      </div>
    </div>
    
    <!-- Vulnerabilities -->
    <div class="mt-6">
      <h4 class="text-lg font-medium mb-2">Vulnerabilities</h4>
      <div class="bg-gray-50 p-3 rounded-md">
        {#if vulnerabilities.length === 0}
          <p class="text-gray-500 italic">No vulnerabilities available</p>
        {:else}
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
            {#each vulnerabilities as vulnerability}
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id={vulnerability.vulnerability_id}
                  checked={selectedVulnerabilities.includes(vulnerability.vulnerability_id)}
                  on:change={() => toggleVulnerability(vulnerability.vulnerability_id)}
                  class="mr-2"
                />
                <label for={vulnerability.vulnerability_id} class="text-sm">
                  <span class={`inline-block w-2 h-2 rounded-full mr-1 bg-${vulnerability.severity.toLowerCase() === 'high' ? 'red' : vulnerability.severity.toLowerCase() === 'medium' ? 'yellow' : 'blue'}-500`}></span>
                  {vulnerability.name}
                </label>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Analysis Button -->
    <div class="mt-6 flex justify-end">
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        on:click={generateAnalysis}
        disabled={loading || !selectedComponentId || selectedComponents.length === 0}
      >
        {loading ? 'Analyzing...' : 'Generate Attack Paths'}
      </button>
    </div>
  </div>
  
  <!-- Analysis Results -->
  {#if analysisResult}
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-xl font-semibold mb-4">Analysis Results</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-gray-50 p-4 rounded-md">
          <p class="text-sm text-gray-500">Analysis ID</p>
          <p class="font-medium">{analysisResult.analysis_id}</p>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-md">
          <p class="text-sm text-gray-500">Components Analyzed</p>
          <p class="font-bold text-xl">{analysisResult.component_count}</p>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-md">
          <p class="text-sm text-gray-500">Attack Paths Found</p>
          <p class="font-bold text-xl">{analysisResult.total_paths}</p>
          <p class="text-xs text-red-500">{analysisResult.high_risk_paths} high risk</p>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-md">
          <p class="text-sm text-gray-500">Attack Chains Found</p>
          <p class="font-bold text-xl">{analysisResult.total_chains}</p>
          <p class="text-xs text-red-500">{analysisResult.high_risk_chains} high risk</p>
        </div>
      </div>
      
      <!-- Entry Points & Targets -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h4 class="text-lg font-medium mb-2">Entry Points</h4>
          <div class="bg-gray-50 p-3 rounded-md">
            {#if analysisResult.entry_points.length === 0}
              <p class="text-gray-500 italic">No entry points identified</p>
            {:else}
              <ul class="space-y-2">
                {#each analysisResult.entry_points as entryPoint}
                  <li class="p-2 bg-blue-50 rounded border border-blue-100">
                    <p class="font-medium">{entryPoint.name}</p>
                    <p class="text-xs text-gray-500">
                      {entryPoint.component_id} - {entryPoint.type} - {entryPoint.trust_zone || 'Unknown zone'}
                    </p>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
        
        <div>
          <h4 class="text-lg font-medium mb-2">Critical Targets</h4>
          <div class="bg-gray-50 p-3 rounded-md">
            {#if analysisResult.critical_targets.length === 0}
              <p class="text-gray-500 italic">No critical targets identified</p>
            {:else}
              <ul class="space-y-2">
                {#each analysisResult.critical_targets as target}
                  <li class="p-2 bg-red-50 rounded border border-red-100">
                    <p class="font-medium">{target.name}</p>
                    <p class="text-xs text-gray-500">
                      {target.component_id} - {target.type} - {target.safety_level || 'No safety level'}
                    </p>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      </div>
      
      <div class="text-center mt-4">
        <a 
          href={`/attack-paths/${analysisResult.analysis_id}`}
          class="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          View Detailed Analysis
        </a>
      </div>
    </div>
  {/if}
  
  {#if loading}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <Loading message="Generating attack paths..." />
      </div>
    </div>
  {/if}
</div>
