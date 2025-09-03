<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Search, Link, Plus, Shield, ExternalLink } from '@lucide/svelte';
  import { safeApiCall } from '../../utils/error-handler';

  export let damageScenarioId: string | null = null;
  export let selectedThreatId: string | null = null;
  export let disabled = false;

  const dispatch = createEventDispatcher();

  let threatScenarios: Array<{
    threat_id: string;
    name: string;
    description?: string;
    attack_vector?: string;
    likelihood?: string;
    impact?: string;
  }> = [];
  let filteredThreats: typeof threatScenarios = [];
  let searchTerm = '';
  let isLoading = true;
  let error = '';
  let showCreateForm = false;
  let newThreatName = '';
  let newThreatDescription = '';
  let isCreating = false;

  onMount(async () => {
    await loadThreatScenarios();
  });

  async function loadThreatScenarios() {
    isLoading = true;
    error = '';
    
    try {
      // Mock API call - replace with actual threat scenarios API
      const result = await safeApiCall(() => 
        fetch('/api/threat-scenarios').then(res => {
          if (!res.ok) throw new Error('Failed to load threat scenarios');
          return res.json();
        })
      );
      
      if (result) {
        threatScenarios = result.threats || [];
        filteredThreats = threatScenarios;
      }
    } catch (err) {
      console.error('Error loading threat scenarios:', err);
      // Mock data for testing
      threatScenarios = [
        {
          threat_id: 'THR-001',
          name: 'CAN Bus Injection Attack',
          description: 'Unauthorized injection of malicious messages into CAN bus',
          attack_vector: 'Network',
          likelihood: 'Medium',
          impact: 'High'
        },
        {
          threat_id: 'THR-002', 
          name: 'ECU Firmware Tampering',
          description: 'Modification of ECU firmware to alter functionality',
          attack_vector: 'Physical',
          likelihood: 'Low',
          impact: 'Critical'
        },
        {
          threat_id: 'THR-003',
          name: 'Memory Corruption Attack',
          description: 'Buffer overflow or memory corruption vulnerabilities',
          attack_vector: 'Software',
          likelihood: 'Medium',
          impact: 'High'
        }
      ];
      filteredThreats = threatScenarios;
    } finally {
      isLoading = false;
    }
  }

  function handleSearch() {
    if (!searchTerm.trim()) {
      filteredThreats = threatScenarios;
      return;
    }

    const term = searchTerm.toLowerCase();
    filteredThreats = threatScenarios.filter(threat =>
      threat.name.toLowerCase().includes(term) ||
      threat.description?.toLowerCase().includes(term) ||
      threat.attack_vector?.toLowerCase().includes(term)
    );
  }

  function selectThreat(threat: typeof threatScenarios[0]) {
    if (disabled) return;
    
    selectedThreatId = threat.threat_id;
    dispatch('threatSelected', {
      threatId: threat.threat_id,
      threatName: threat.name,
      threatDescription: threat.description
    });
  }

  function clearSelection() {
    selectedThreatId = null;
    dispatch('threatCleared');
  }

  async function createNewThreat() {
    if (!newThreatName.trim()) return;
    
    isCreating = true;
    
    try {
      // Mock API call - replace with actual create threat API
      const newThreat = {
        threat_id: `THR-${Date.now()}`,
        name: newThreatName,
        description: newThreatDescription,
        attack_vector: 'Unknown',
        likelihood: 'Medium',
        impact: 'Medium'
      };
      
      threatScenarios = [newThreat, ...threatScenarios];
      filteredThreats = threatScenarios;
      
      // Auto-select the new threat
      selectThreat(newThreat);
      
      // Reset form
      showCreateForm = false;
      newThreatName = '';
      newThreatDescription = '';
      
      dispatch('threatCreated', newThreat);
    } catch (err) {
      console.error('Error creating threat scenario:', err);
      error = 'Failed to create threat scenario. Please try again.';
    } finally {
      isCreating = false;
    }
  }

  function cancelCreate() {
    showCreateForm = false;
    newThreatName = '';
    newThreatDescription = '';
  }

  $: handleSearch();
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h3 class="text-lg font-medium text-gray-900">Link Threat Scenario</h3>
      <p class="text-sm text-gray-600">Connect this damage scenario to a threat scenario</p>
    </div>
    {#if selectedThreatId}
      <button
        on:click={clearSelection}
        class="text-sm text-red-600 hover:text-red-700 transition-colors"
        disabled={disabled}
      >
        Clear Link
      </button>
    {/if}
  </div>

  <!-- Action Buttons -->
  <div class="flex space-x-2">
    <button
      on:click={() => showCreateForm = !showCreateForm}
      disabled={disabled}
      class="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Plus class="h-4 w-4" />
      <span>Create New Threat</span>
    </button>
  </div>

  <!-- Create New Threat Form -->
  {#if showCreateForm}
    <div class="bg-gray-50 border border-gray-200 rounded-md p-4 space-y-3">
      <h4 class="font-medium text-gray-900">Create New Threat Scenario</h4>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
        <input
          type="text"
          bind:value={newThreatName}
          placeholder="Enter threat scenario name"
          disabled={isCreating}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          bind:value={newThreatDescription}
          placeholder="Describe the threat scenario"
          rows="3"
          disabled={isCreating}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        ></textarea>
      </div>
      
      <div class="flex space-x-2">
        <button
          on:click={createNewThreat}
          disabled={!newThreatName.trim() || isCreating}
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {#if isCreating}
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {:else}
            <Plus class="h-4 w-4" />
          {/if}
          <span>Create & Link</span>
        </button>
        <button
          on:click={cancelCreate}
          disabled={isCreating}
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  {/if}

  <!-- Search -->
  <div class="relative">
    <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
    <input
      type="text"
      bind:value={searchTerm}
      placeholder="Search existing threat scenarios..."
      disabled={disabled}
      class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
    />
  </div>

  <!-- Loading State -->
  {#if isLoading}
    <div class="text-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-600 text-sm mt-2">Loading threat scenarios...</p>
    </div>
  {:else if error}
    <!-- Error State -->
    <div class="bg-red-50 border border-red-200 rounded-md p-4">
      <p class="text-red-700 text-sm">{error}</p>
      <button 
        on:click={loadThreatScenarios}
        class="mt-2 text-sm text-red-600 hover:text-red-700 underline"
      >
        Retry
      </button>
    </div>
  {:else if filteredThreats.length === 0}
    <!-- Empty State -->
    <div class="text-center py-8">
      <Shield class="mx-auto h-12 w-12 text-gray-300 mb-3" />
      <h4 class="text-sm font-medium text-gray-900 mb-1">No threat scenarios found</h4>
      <p class="text-sm text-gray-600">
        {searchTerm ? 'Try adjusting your search terms or create a new threat scenario.' : 'Create your first threat scenario.'}
      </p>
    </div>
  {:else}
    <!-- Threat Scenarios List -->
    <div class="space-y-2 max-h-64 overflow-y-auto">
      {#each filteredThreats as threat}
        <button
          on:click={() => selectThreat(threat)}
          disabled={disabled}
          class="w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
            {selectedThreatId === threat.threat_id ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : ''}"
          data-testid="threat-option-{threat.threat_id}"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <Shield class="h-4 w-4 text-gray-500" />
                <h4 class="font-medium text-gray-900">{threat.name}</h4>
                {#if selectedThreatId === threat.threat_id}
                  <Link class="h-4 w-4 text-blue-600" />
                {/if}
              </div>
              {#if threat.description}
                <p class="text-sm text-gray-600 mt-1 line-clamp-2">{threat.description}</p>
              {/if}
              
              <div class="flex space-x-2 mt-2">
                {#if threat.attack_vector}
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {threat.attack_vector}
                  </span>
                {/if}
                {#if threat.likelihood}
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                    {threat.likelihood} Likelihood
                  </span>
                {/if}
                {#if threat.impact}
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium 
                    {threat.impact === 'Critical' ? 'bg-red-100 text-red-800' : 
                     threat.impact === 'High' ? 'bg-orange-100 text-orange-800' : 
                     'bg-blue-100 text-blue-800'}">
                    {threat.impact} Impact
                  </span>
                {/if}
              </div>
            </div>
            <ExternalLink class="h-4 w-4 text-gray-400" />
          </div>
        </button>
      {/each}
    </div>
  {/if}

  <!-- Selection Summary -->
  {#if selectedThreatId}
    <div class="bg-green-50 border border-green-200 rounded-md p-3">
      <div class="flex items-center">
        <Link class="h-5 w-5 text-green-600 mr-2" />
        <div>
          <p class="text-sm font-medium text-green-800">Threat Scenario Linked</p>
          <p class="text-sm text-green-700">
            {filteredThreats.find(t => t.threat_id === selectedThreatId)?.name || 'Selected threat'}
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
