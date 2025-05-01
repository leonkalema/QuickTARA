<!-- Attack Path Visualization Component -->
<script>
  import { onMount, afterUpdate } from 'svelte';
  import * as d3 from 'd3';
  import { getAttackPaths, getAttackPath } from '../../api/attackPath';
  
  // Props
  export let analysisId = '';
  export let selectedPathId = '';
  export let pathData = null;
  
  // Component state
  let container;
  let loading = false;
  let error = null;
  let paths = [];
  let width = 800;
  let height = 600;
  
  // Watch for changes to selected path ID
  $: if (selectedPathId) {
    fetchPathDetails(selectedPathId);
  }
  
  onMount(async () => {
    if (analysisId) {
      await fetchPaths(analysisId);
    }
    
    if (pathData) {
      renderPath(pathData);
    }
    
    // Handle resize
    const resizeObserver = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === container) {
          width = entry.contentRect.width;
          height = Math.max(500, entry.contentRect.height);
          if (pathData) {
            renderPath(pathData);
          }
        }
      }
    });
    
    if (container) {
      resizeObserver.observe(container);
    }
    
    return () => {
      if (container) {
        resizeObserver.unobserve(container);
      }
    };
  });
  
  afterUpdate(() => {
    if (pathData && container) {
      renderPath(pathData);
    }
  });
  
  async function fetchPaths(analysisId) {
    try {
      loading = true;
      error = null;
      
      // Fetch paths for this analysis
      const result = await getAttackPaths(analysisId);
      paths = result.paths || [];
      
      // If paths are available and no path is selected, select the first one
      if (paths.length > 0 && !selectedPathId) {
        selectedPathId = paths[0].path_id;
        await fetchPathDetails(selectedPathId);
      }
      
      loading = false;
    } catch (err) {
      console.error('Error fetching attack paths:', err);
      error = `Failed to fetch attack paths: ${err.message || 'Unknown error'}`;
      loading = false;
    }
  }
  
  async function fetchPathDetails(pathId) {
    try {
      loading = true;
      error = null;
      
      // Fetch details for this path
      const path = await getAttackPath(pathId);
      pathData = path;
      
      loading = false;
    } catch (err) {
      console.error(`Error fetching attack path ${pathId}:`, err);
      error = `Failed to fetch attack path details: ${err.message || 'Unknown error'}`;
      loading = false;
    }
  }
  
  function renderPath(path) {
    if (!path || !container) return;
    
    // Clear previous visualization
    d3.select(container).selectAll('*').remove();
    
    // Create SVG element
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height])
      .attr('style', 'max-width: 100%; height: auto;');
      
    // Sort steps by order
    const steps = [...path.steps].sort((a, b) => a.order - b.order);
    
    // Define node size and spacing
    const nodeWidth = 150;
    const nodeHeight = 80;
    const horizontalSpacing = width / (steps.length + 1);
    const verticalCenter = height / 2;
    
    // Create a group for each step
    const groups = svg.selectAll('g')
      .data(steps)
      .enter()
      .append('g')
      .attr('transform', (d, i) => `translate(${(i + 1) * horizontalSpacing - nodeWidth/2}, ${verticalCenter - nodeHeight/2})`);
    
    // Draw node background based on step type
    groups.append('rect')
      .attr('width', nodeWidth)
      .attr('height', nodeHeight)
      .attr('rx', 5)
      .attr('ry', 5)
      .attr('fill', d => {
        // Color based on step type
        switch(d.step_type) {
          case 'Initial Access': return '#e3f2fd'; // Light blue
          case 'Execution': return '#e8f5e9'; // Light green
          case 'Privilege Escalation': return '#fff3e0'; // Light orange
          case 'Lateral Movement': return '#f3e5f5'; // Light purple
          case 'Impact': return '#ffebee'; // Light red
          default: return '#f5f5f5'; // Light gray
        }
      })
      .attr('stroke', d => {
        // Border color based on step type
        switch(d.step_type) {
          case 'Initial Access': return '#2196f3'; // Blue
          case 'Execution': return '#4caf50'; // Green
          case 'Privilege Escalation': return '#ff9800'; // Orange
          case 'Lateral Movement': return '#9c27b0'; // Purple
          case 'Impact': return '#f44336'; // Red
          default: return '#9e9e9e'; // Gray
        }
      })
      .attr('stroke-width', 2);
      
    // Add step type label
    groups.append('text')
      .attr('x', nodeWidth / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .text(d => d.step_type);
      
    // Add component ID
    groups.append('text')
      .attr('x', nodeWidth / 2)
      .attr('y', 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .text(d => d.component_id);
      
    // Add description (truncated if necessary)
    groups.append('text')
      .attr('x', nodeWidth / 2)
      .attr('y', 50)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .text(d => {
        const maxLength = 25;
        return d.description.length > maxLength 
          ? d.description.substring(0, maxLength) + '...' 
          : d.description;
      });
      
    // Add vulnerability indicators if present
    groups.filter(d => d.vulnerability_ids && d.vulnerability_ids.length > 0)
      .append('circle')
      .attr('cx', nodeWidth - 10)
      .attr('cy', 10)
      .attr('r', 5)
      .attr('fill', '#f44336') // Red for vulnerability
      .append('title')
      .text(d => `Vulnerabilities: ${d.vulnerability_ids.join(', ')}`);
    
    // Draw arrows between nodes
    for (let i = 0; i < steps.length - 1; i++) {
      svg.append('path')
        .attr('d', `M${(i + 1) * horizontalSpacing + nodeWidth/2},${verticalCenter} L${(i + 2) * horizontalSpacing - nodeWidth/2},${verticalCenter}`)
        .attr('stroke', '#757575')
        .attr('stroke-width', 2)
        .attr('marker-end', 'url(#arrow)');
    }
    
    // Define arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#757575');
      
    // Add path metadata to the top
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(path.name);
      
    // Add risk information
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 50)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .text(`Risk: ${path.risk_score.toFixed(1)} | Complexity: ${path.complexity} | Success Likelihood: ${(path.success_likelihood * 100).toFixed(0)}%`);
  }
</script>

<div class="attack-path-visualizer">
  {#if error}
    <div class="error-message p-3 bg-red-100 text-red-700 rounded-md mb-4">
      {error}
    </div>
  {/if}
  
  {#if loading}
    <div class="loading p-8 text-center">
      <p>Loading attack path visualization...</p>
    </div>
  {:else if pathData}
    <div class="visualization-container" bind:this={container}></div>
    
    {#if pathData.steps && pathData.steps.length > 0}
      <div class="path-details mt-6">
        <h3 class="text-xl font-semibold mb-2">Attack Path Details</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Risk Score</h4>
            <p class="text-2xl font-bold" class:text-red-600={pathData.risk_score >= 7} class:text-yellow-600={pathData.risk_score >= 4 && pathData.risk_score < 7} class:text-green-600={pathData.risk_score < 4}>
              {pathData.risk_score.toFixed(1)}
            </p>
          </div>
          
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Complexity</h4>
            <p class="text-2xl font-bold">
              {pathData.complexity}
            </p>
          </div>
          
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Success Likelihood</h4>
            <p class="text-2xl font-bold">
              {(pathData.success_likelihood * 100).toFixed(0)}%
            </p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Confidentiality Impact</h4>
            <p class="text-2xl font-bold" class:text-red-600={pathData.impact.confidentiality >= 7} class:text-yellow-600={pathData.impact.confidentiality >= 4 && pathData.impact.confidentiality < 7} class:text-green-600={pathData.impact.confidentiality < 4}>
              {pathData.impact.confidentiality}/10
            </p>
          </div>
          
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Integrity Impact</h4>
            <p class="text-2xl font-bold" class:text-red-600={pathData.impact.integrity >= 7} class:text-yellow-600={pathData.impact.integrity >= 4 && pathData.impact.integrity < 7} class:text-green-600={pathData.impact.integrity < 4}>
              {pathData.impact.integrity}/10
            </p>
          </div>
          
          <div class="p-3 bg-gray-50 rounded-md">
            <h4 class="font-medium text-gray-700">Availability Impact</h4>
            <p class="text-2xl font-bold" class:text-red-600={pathData.impact.availability >= 7} class:text-yellow-600={pathData.impact.availability >= 4 && pathData.impact.availability < 7} class:text-green-600={pathData.impact.availability < 4}>
              {pathData.impact.availability}/10
            </p>
          </div>
        </div>
        
        <!-- Steps Details -->
        <div class="mt-6">
          <h4 class="font-medium text-gray-700 mb-2">Attack Steps</h4>
          <div class="space-y-2">
            {#each pathData.steps.sort((a, b) => a.order - b.order) as step}
              <div class="p-3 bg-gray-50 rounded-md">
                <div class="flex items-center mb-1">
                  <span class="px-2 py-1 text-xs font-medium rounded mr-2" 
                    class:bg-blue-100={step.step_type === 'Initial Access'}
                    class:bg-green-100={step.step_type === 'Execution'}
                    class:bg-orange-100={step.step_type === 'Privilege Escalation'}
                    class:bg-purple-100={step.step_type === 'Lateral Movement'}
                    class:bg-red-100={step.step_type === 'Impact'}
                    class:bg-gray-100={!['Initial Access', 'Execution', 'Privilege Escalation', 'Lateral Movement', 'Impact'].includes(step.step_type)}
                  >
                    {step.step_type}
                  </span>
                  <span class="text-sm font-medium">{step.component_id}</span>
                </div>
                <p class="text-sm">{step.description}</p>
                
                {#if step.vulnerability_ids && step.vulnerability_ids.length > 0}
                  <div class="mt-2">
                    <h5 class="text-xs font-medium text-gray-700">Vulnerabilities:</h5>
                    <div class="flex flex-wrap gap-1 mt-1">
                      {#each step.vulnerability_ids as vulnId}
                        <span class="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                          {vulnId}
                        </span>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/if}
  {:else}
    <div class="no-data p-8 text-center">
      <p class="text-gray-500">No attack path data available.</p>
      {#if analysisId}
        <button 
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          on:click={() => fetchPaths(analysisId)}
        >
          Load Attack Paths
        </button>
      {/if}
    </div>
  {/if}
</div>

<style>
  .visualization-container {
    width: 100%;
    height: 400px;
    overflow: auto;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
  }
  
  .attack-path-visualizer {
    width: 100%;
  }
</style>
