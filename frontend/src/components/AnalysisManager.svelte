<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, RefreshCw, BarChart, AlertTriangle, Shield, Activity, Search, ShieldAlert, Zap } from '@lucide/svelte';
  import { analysisApi, type Analysis, AnalysisStatus } from '../api/analysis';
  import { componentApi } from '../api/components';
  import { safeApiCall } from '../utils/error-handler';
  import AnalysisForm from './AnalysisForm.svelte';
  import ThreatAnalysisVisualizer from './threat/ThreatAnalysisVisualizer.svelte';
  import VulnerabilityAssessmentTab from './vulnerability/VulnerabilityAssessmentTab.svelte';
  import DamageScenarioManager from './damage-scenario/DamageScenarioManager.svelte';
  
  // Analysis state
  let analyses: Analysis[] = [];
  let isLoading = true;
  let error = '';
  let showForm = false;
  
  // Active tab management
  let activeTab = 'damage-scenarios'; // 'damage-scenarios', 'general-analysis', 'threat-analysis', 'vulnerability-analysis'
  let selectedComponentIds: string[] = [];
  
  // Summary stats
  let stats = {
    totalAnalyses: 0,
    pendingAnalyses: 0,
    criticalFindings: 0,
    highRiskThreats: 0
  };
  
  onMount(async () => {
    await loadAnalyses();
  });
  
  async function loadAnalyses() {
    isLoading = true;
    error = '';
    
    try {
      const result = await safeApiCall(() => analysisApi.getAll());
      
      if (result) {
        analyses = Array.isArray(result) ? result : [];
        updateStats(analyses);
      }
    } catch (err) {
      console.error('Error loading analyses:', err);
      error = 'Failed to load analyses. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  function updateStats(analyses: Analysis[]) {
    stats.totalAnalyses = analyses.length;
    stats.pendingAnalyses = analyses.filter(a => 
      a.status === AnalysisStatus.PENDING || a.status === AnalysisStatus.RUNNING
    ).length;
    
    // These would be populated from actual analysis results in a full implementation
    stats.criticalFindings = Math.floor(Math.random() * 10); // Placeholder
    stats.highRiskThreats = Math.floor(Math.random() * 20); // Placeholder
  }
  
  function handleStartAnalysis() {
    showForm = true;
  }
  
  function handleFormCancel() {
    showForm = false;
  }
  
  async function handleFormSubmit(event: CustomEvent) {
    const analysisData = event.detail;
    
    try {
      const newAnalysis = await safeApiCall(() => 
        analysisApi.runAnalysis(analysisData)
      );
      
      if (newAnalysis) {
        analyses = [...analyses, newAnalysis];
        showForm = false;
        updateStats(analyses);
      }
    } catch (err) {
      console.error('Error creating analysis:', err);
    }
  }
  
  function getStatusColor(status: AnalysisStatus) {
    switch(status) {
      case AnalysisStatus.COMPLETED:
        return 'text-green-600';
      case AnalysisStatus.RUNNING:
        return 'text-blue-600';
      case AnalysisStatus.PENDING:
        return 'text-yellow-600';
      case AnalysisStatus.FAILED:
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  }
  
  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
</script>

<div class="space-y-6">
  <!-- Tab Navigation -->
  <div class="border-b border-gray-200">
    <nav class="-mb-px flex space-x-8" aria-label="Analysis sections">
      <button
        class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'damage-scenarios' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
        on:click={() => activeTab = 'damage-scenarios'}
      >
        <Zap class="h-5 w-5" />
        <span>Damage Scenarios</span>
      </button>
      
      <button
        class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'general-analysis' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
        on:click={() => activeTab = 'general-analysis'}
      >
        <Activity class="h-5 w-5" />
        <span>Component Analysis</span>
      </button>
      
      <button
        class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'threat-analysis' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
        on:click={() => activeTab = 'threat-analysis'}
      >
        <Shield class="h-5 w-5" />
        <span>Threat Analysis</span>
      </button>
      
      <button
        class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'vulnerability-analysis' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
        on:click={() => activeTab = 'vulnerability-analysis'}
      >
        <ShieldAlert class="h-5 w-5" />
        <span>Vulnerability Assessment</span>
      </button>
    </nav>
  </div>

  {#if activeTab === 'general-analysis'}
  <!-- General Analysis Content -->
  <!-- Stats cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <!-- Analysis Count -->
    <div class="metric-card">
      <div class="flex items-start">
        <BarChart size={24} style="color: var(--color-primary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Total Analyses</p>
          <p class="metric-value">{stats.totalAnalyses}</p>
        </div>
      </div>
    </div>
    
    <!-- Pending Analyses -->
    <div class="metric-card">
      <div class="flex items-start">
        <RefreshCw size={24} style="color: var(--color-secondary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Pending Analyses</p>
          <p class="metric-value">{stats.pendingAnalyses}</p>
        </div>
      </div>
    </div>
    
    <!-- Critical Findings -->
    <div class="metric-card">
      <div class="flex items-start">
        <AlertTriangle size={24} style="color: var(--color-danger);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Critical Findings</p>
          <p class="metric-value">{stats.criticalFindings}</p>
        </div>
      </div>
    </div>
    
    <!-- High Risk Threats -->
    <div class="metric-card">
      <div class="flex items-start">
        <Shield size={24} style="color: var(--color-warning);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">High Risk Threats</p>
          <p class="metric-value">{stats.highRiskThreats}</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">Analysis List</h2>
    
    <div class="flex space-x-2">
      <button 
        on:click={loadAnalyses}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);" 
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
        <RefreshCw size={16} class="{isLoading ? 'animate-spin' : ''}" />
        <span class="sr-only md:not-sr-only">Refresh</span>
      </button>
      
      <button 
        on:click={handleStartAnalysis}
        class="btn btn-primary flex items-center gap-1">
        <Plus size={16} />
        <span>New Analysis</span>
      </button>
    </div>
  </div>
  
  <!-- Analysis List -->
  <div>
    {#if isLoading}
      <div class="flex justify-center items-center h-64">
        <div class="text-center">
          <RefreshCw size={36} class="animate-spin mx-auto text-primary mb-4" />
          <p class="text-gray-600">Loading analyses...</p>
        </div>
      </div>
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 flex items-start">
        <AlertTriangle size={20} class="mr-3 mt-0.5 flex-shrink-0" />
        <div>
          <h3 class="font-medium">Error loading analyses</h3>
          <p class="mt-1">{error}</p>
          <button 
            on:click={loadAnalyses}
            class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 flex items-center gap-1">
            <RefreshCw size={14} /> Try again
          </button>
        </div>
      </div>
    {:else if analyses.length === 0}
      <div class="bg-gray-50 border border-gray-200 text-gray-600 rounded-lg p-8 text-center">
        <p class="mb-4">No analyses found. Run your first analysis to get started.</p>
        <button 
          on:click={handleStartAnalysis}
          class="btn btn-primary inline-flex items-center gap-1">
          <Plus size={16} />
          <span>New Analysis</span>
        </button>
      </div>
    {:else}
      <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Components
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created At
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each analyses as analysis}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{analysis.name}</div>
                  {#if analysis.description}
                    <div class="text-sm text-gray-500">{analysis.description}</div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    {analysis.component_ids?.length || 0} components
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getStatusColor(analysis.status)} bg-opacity-10">
                    {analysis.status}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(analysis.created_at)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <a href={`/analysis/${analysis.id}`} class="text-indigo-600 hover:text-indigo-900 mr-3">View</a>
                  <button class="text-red-600 hover:text-red-900">Delete</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
  
  <!-- Analysis Form Dialog -->
  {#if showForm}
    <div class="fixed inset-0 backdrop-blur-sm bg-neutral-900/40 flex items-center justify-center z-50 p-4 transition-opacity duration-200">
      <div class="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <AnalysisForm
          on:submit={handleFormSubmit}
          on:cancel={handleFormCancel}
        />
      </div>
    </div>
  {/if}
  {/if}
  
  <!-- Threat Analysis Tab Content -->
  {#if activeTab === 'threat-analysis'}
    <ThreatAnalysisVisualizer bind:selectedComponentIds={selectedComponentIds} />
  {/if}
  
  <!-- Vulnerability Assessment Tab Content -->
  {#if activeTab === 'vulnerability-analysis'}
    <VulnerabilityAssessmentTab />
  {/if}
  
  <!-- Damage Scenarios Tab Content -->
  {#if activeTab === 'damage-scenarios'}
    <DamageScenarioManager />
  {/if}
</div>

<style>
  .metric-card {
    background-color: var(--color-card-bg);
    border: 1px solid var(--color-border);
    padding: 1.25rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  .metric-label {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }
  
  .metric-value {
    color: var(--color-text-main);
    font-size: 1.5rem;
    font-weight: 600;
  }
</style>
