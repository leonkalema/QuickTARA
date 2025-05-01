# Attack Path Analysis Components

This directory contains the components for visualizing and interacting with attack paths and chains in the QuickTARA application.

## Components Overview

- `AttackPathManager.svelte`: The main container component that handles loading and managing attack paths and chains.
- `AttackPathList.svelte`: Displays a list of attack paths with their key details and handles selection.
- `AttackChainList.svelte`: Displays a list of attack chains with their key details and handles selection.
- `AttackPathVisualization.svelte`: Visualizes attack paths and chains as interactive graphs using D3.js.

## Features

- Interactive graph-based visualization of attack paths
- Filtering by complexity level
- Tab-based navigation between paths and chains
- Color-coded nodes based on step types
- Risk scoring visualization
- Drag-and-drop functionality for rearranging nodes

## Visualization Logic

The visualization uses D3.js to create a force-directed graph representation of attack paths and chains. Each node represents a component in the attack path, and each link represents a step in the attack process. The visualization is interactive, allowing for:

- Dragging nodes to rearrange the layout
- Hovering over nodes to see details
- Visually distinguishing entry points and targets
- Color-coding based on attack step types

## Integration Points

These components integrate with the backend through the API client defined in `src/api/attackPath.ts`, which provides functions for:

- Generating attack paths
- Retrieving attack paths and chains
- Getting detailed information about specific paths and chains

## Usage

To use these components, add the `AttackPathManager` to a page or tab in the application. It will handle loading data and rendering the appropriate sub-components.

```svelte
<script>
  import AttackPathManager from '../components/attack-path/AttackPathManager.svelte';
</script>

<AttackPathManager />
```

## Dependencies

This component requires D3.js for visualization. Make sure to add D3.js to the project dependencies:

```bash
npm install d3
```

And add types for TypeScript support:

```bash
npm install @types/d3 --save-dev
```
