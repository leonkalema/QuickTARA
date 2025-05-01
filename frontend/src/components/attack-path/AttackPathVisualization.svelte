<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import * as d3 from 'd3';
  import type { AttackPath, AttackChain, AttackStepType } from '../../api/attackPath';
  
  export let path: AttackPath | null = null;
  export let chain: AttackChain | null = null;

  // Visualization dimensions and settings
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };
  const nodeRadius = 30;
  const nodeStrokeWidth = 2;
  const arrowSize = 10;
  let width = 0;
  let height = 600;
  let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  let container: HTMLDivElement;
  
  // Node and link data for the visualization
  let nodes: any[] = [];
  let links: any[] = [];
  
  // Step type icon mapping
  const stepTypeIcons: Record<AttackStepType, string> = {
    'Initial Access': '🔑',
    'Execution': '⚙️',
    'Persistence': '🔄',
    'Privilege Escalation': '⬆️',
    'Defense Evasion': '🛡️',
    'Credential Access': '🔒',
    'Discovery': '🔍',
    'Lateral Movement': '↔️',
    'Collection': '📦',
    'Exfiltration': '📤',
    'Command and Control': '🎮',
    'Impact': '💥'
  };
  
  // Step type color mapping
  const stepTypeColors: Record<AttackStepType, string> = {
    'Initial Access': '#4299e1',
    'Execution': '#48bb78',
    'Persistence': '#ecc94b',
    'Privilege Escalation': '#ed8936',
    'Defense Evasion': '#667eea',
    'Credential Access': '#ed64a6',
    'Discovery': '#9f7aea',
    'Lateral Movement': '#38b2ac',
    'Collection': '#f56565',
    'Exfiltration': '#e53e3e',
    'Command and Control': '#d69e2e',
    'Impact': '#9b2c2c'
  };
  
  // Risk score color scale
  const riskColorScale = d3.scaleSequential()
    .domain([0, 10])
    .interpolator(d3.interpolateRgb('#38a169', '#e53e3e'));
  
  // Process data when path or chain changes
  $: if (path) {
    console.log('Processing attack path with steps:', path.steps?.length || 0);
    console.log('Attack path data:', path);
    processPathData(path);
  } else if (chain) {
    console.log('Processing attack chain with paths:', chain.paths?.length || 0);
    console.log('Attack chain data:', chain);
    processChainData(chain);
  }
  
  // Update visualization when container size changes
  $: if (container) {
    width = container.clientWidth;
  }
  
  // Initialize visualization on mount
  onMount(() => {
    if (container) {
      width = container.clientWidth;
    }
    initVisualization();
  });
  
  // Update visualization after data changes
  afterUpdate(() => {
    if (svg && (path || chain)) {
      updateVisualization();
    }
  });
  
  // Process attack path data into nodes and links
  function processPathData(path: AttackPath) {
    nodes = [];
    links = [];
    
    // Check if the path has steps
    if (!path.steps || !Array.isArray(path.steps) || path.steps.length === 0) {
      console.error('Path is missing steps data:', path);
      // Create minimal representation with just entry point and target
      nodes.push({
        id: path.entry_point_id,
        label: path.entry_point_id,
        description: 'Entry point',
        type: 'Initial Access' as AttackStepType,
        order: 0,
        isFirstStep: true,
        isLastStep: false
      });
      
      nodes.push({
        id: path.target_id,
        label: path.target_id,
        description: 'Target',
        type: 'Impact' as AttackStepType,
        order: 1,
        isFirstStep: false,
        isLastStep: true
      });
      
      links.push({
        source: path.entry_point_id,
        target: path.target_id,
        type: 'Impact' as AttackStepType
      });
      
      return;
    }
    
    // Add nodes for each step in the path
    path.steps.forEach((step, index) => {
      nodes.push({
        id: step.component_id,
        label: step.component_id,
        description: step.description,
        type: step.step_type,
        step: step,
        order: step.order,
        isFirstStep: index === 0,
        isLastStep: index === path.steps.length - 1
      });
      
      // Add links between steps
      if (index < path.steps.length - 1) {
        links.push({
          source: step.component_id,
          target: path.steps[index + 1].component_id,
          type: path.steps[index + 1].step_type
        });
      }
    });
  }
  
  // Process attack chain data into nodes and links
  function processChainData(chain: AttackChain) {
    nodes = [];
    links = [];
    
    // Process each path in the chain
    if (chain.paths && Array.isArray(chain.paths) && chain.paths.length > 0) {
      // Create a map of component IDs to prevent duplicate nodes
      const componentMap = new Map();
      
      // Process each path and connect them
      chain.paths.forEach((path, pathIndex) => {
        // Check if the path has steps
        if (!path.steps || !Array.isArray(path.steps) || path.steps.length === 0) {
          console.error('Path in chain is missing steps data:', path);
          // Create minimal representation with just entry point and target
          if (!componentMap.has(path.entry_point_id)) {
            componentMap.set(path.entry_point_id, {
              id: path.entry_point_id,
              label: path.entry_point_id,
              description: 'Entry point',
              type: 'Initial Access' as AttackStepType,
              order: 0,
              isFirstStep: path.entry_point_id === chain.entry_point_id,
              isLastStep: false
            });
            nodes.push(componentMap.get(path.entry_point_id));
          }
          
          if (!componentMap.has(path.target_id)) {
            componentMap.set(path.target_id, {
              id: path.target_id,
              label: path.target_id,
              description: 'Target',
              type: 'Impact' as AttackStepType,
              order: 1,
              isFirstStep: false,
              isLastStep: path.target_id === chain.final_target_id
            });
            nodes.push(componentMap.get(path.target_id));
          }
          
          links.push({
            source: path.entry_point_id,
            target: path.target_id,
            type: 'Impact' as AttackStepType,
            pathIndex: pathIndex
          });
          
          return;
        }
        
        path.steps.forEach((step, stepIndex) => {
          // Add node if it doesn't exist
          if (!componentMap.has(step.component_id)) {
            componentMap.set(step.component_id, {
              id: step.component_id,
              label: step.component_id,
              description: step.description,
              type: step.step_type,
              step: step,
              order: step.order,
              isFirstStep: step.component_id === chain.entry_point_id,
              isLastStep: step.component_id === chain.final_target_id
            });
            
            nodes.push(componentMap.get(step.component_id));
          }
          
          // Add links between steps in the same path
          if (stepIndex < path.steps.length - 1) {
            links.push({
              source: step.component_id,
              target: path.steps[stepIndex + 1].component_id,
              type: path.steps[stepIndex + 1].step_type,
              pathIndex: pathIndex
            });
          }
        });
      });
    } else {
      console.error('Chain is missing paths data or has empty paths:', chain);
      // Create minimal representation with just entry point and target
      if (chain.entry_point_id && chain.final_target_id) {
        nodes.push({
          id: chain.entry_point_id,
          label: chain.entry_point_id,
          description: 'Chain entry point',
          type: 'Initial Access' as AttackStepType,
          order: 0,
          isFirstStep: true,
          isLastStep: false
        });
        
        nodes.push({
          id: chain.final_target_id,
          label: chain.final_target_id,
          description: 'Chain target',
          type: 'Impact' as AttackStepType,
          order: 1,
          isFirstStep: false,
          isLastStep: true
        });
        
        links.push({
          source: chain.entry_point_id,
          target: chain.final_target_id,
          type: 'Impact' as AttackStepType,
          pathIndex: 0
        });
      }
    }
  }
  
  // Initialize the visualization container
  function initVisualization() {
    // Clear any existing visualization
    if (container) {
      container.innerHTML = '';
    }
    
    // Create SVG container
    svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
      
    // Add marker definitions for arrows
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', nodeRadius + 15)
      .attr('refY', 0)
      .attr('markerWidth', arrowSize)
      .attr('markerHeight', arrowSize)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#666');
      
    // Update the visualization with data
    updateVisualization();
  }
  
  // Update the visualization with new data
  function updateVisualization() {
    if (!svg || (!path && !chain) || nodes.length === 0) {
      return;
    }
    
    // Clear previous elements
    svg.selectAll('*').remove();
    
    // Add marker definition for arrows
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', nodeRadius + 15)
      .attr('refY', 0)
      .attr('markerWidth', arrowSize)
      .attr('markerHeight', arrowSize)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#666');
      
    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-500))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(nodeRadius * 2));
      
    // Create links
    const link = svg.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(links)
      .enter().append('path')
      .attr('stroke', (d: any) => {
        const stepType = d.type as AttackStepType;
        return stepTypeColors[stepType] || '#999';
      })
      .attr('stroke-width', 2)
      .attr('fill', 'none')
      .attr('marker-end', 'url(#arrowhead)');
      
    // Create nodes
    const node = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('.node')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));
        
    // Add circle for each node
    node.append('circle')
      .attr('r', nodeRadius)
      .attr('fill', (d: any) => {
        if (d.isFirstStep) return '#4299e1';
        if (d.isLastStep) return '#f56565';
        const stepType = d.type as AttackStepType;
        return stepTypeColors[stepType] || '#999';
      })
      .attr('stroke', (d: any) => d.isFirstStep || d.isLastStep ? '#000' : '#666')
      .attr('stroke-width', nodeStrokeWidth);
      
    // Add icon for each node
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '1.2em')
      .text((d: any) => {
        const stepType = d.type as AttackStepType;
        return stepTypeIcons[stepType] || '❓';
      });
      
    // Add label for each node
    node.append('text')
      .attr('dy', nodeRadius + 20)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#333')
      .attr('pointer-events', 'none')
      .text((d: any) => d.label);
      
    // Add tooltips for nodes
    node.append('title')
      .text((d: any) => `${d.label}\nType: ${d.type}\n${d.description}`);
      
    // Update positions on simulation tick
    simulation.on('tick', () => {
      link.attr('d', (d: any) => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });
      
      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });
    
    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }
</script>

<div class="bg-white rounded-lg shadow-md overflow-hidden h-full">
  <div class="p-4 bg-blue-50 border-b border-blue-100">
    <h2 class="text-lg font-semibold text-gray-800">
      {#if path}
        {path.name}
      {:else if chain}
        {chain.name}
      {:else}
        Attack Path Visualization
      {/if}
    </h2>
    {#if path && (!path.steps || !path.steps.length)}
      <div class="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
        Note: Detailed step data is missing for this path. Showing simplified visualization.
      </div>
    {/if}
  </div>
  
  <div class="h-[calc(100%-4rem)]" bind:this={container}>
    {#if !path && !chain}
      <div class="flex items-center justify-center h-full">
        <p class="text-gray-500">Select an attack path or chain to visualize</p>
      </div>
    {/if}
  </div>
</div>

<style>
  /* Make sure SVG fills the container properly but scoped to this component */
  div :global(svg) {
    width: 100%;
    height: 100%;
    display: block;
  }
</style>
