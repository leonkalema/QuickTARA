# QuickTARA Component Management UI

This directory contains the implementation of the Component Management UI for QuickTARA, a tool for automotive security analysis.

## Overview

The Component Management UI provides a modern, user-friendly interface for managing automotive components within the QuickTARA system. It follows a modular design with clear separation of concerns and adheres to the project's coding standards.

## Key Features

- **Component List**: View, filter, and manage all components
- **Component Card**: Display component information in an attractive card format
- **Component Form**: Add and edit components with a comprehensive form
- **Component Import**: Import components from CSV files
- **Component Filtering**: Filter components by various attributes
- **Statistics Dashboard**: View key metrics about your components

## Components

### ComponentManager.svelte

The main container component that orchestrates the component management workflow. It provides:

- A statistics dashboard at the top to show key metrics
- Tab navigation for different sections of the application
- Content area for displaying the active module

### ComponentList.svelte

Displays the list of components with filtering and management capabilities:

- Table of components with search and filtering
- Actions for adding, editing, and deleting components
- Import/export functionality for CSV files
- Error handling and loading states

### ComponentCard.svelte

A visually appealing card that displays key information about a component:

- Component name, ID, and type with appropriate icons
- Safety level with color-coded badges
- Trust zone information
- Quick actions for editing and deleting

### ComponentForm.svelte

A comprehensive form for adding and editing components:

- Input fields for all component attributes
- Dynamic arrays for interfaces, access points, and data types
- Validation and error handling
- Responsive layout

### ComponentFilter.svelte

A filtering interface for the component list:

- Search by name or ID
- Filter by component type
- Filter by safety level
- Filter by trust zone

### ComponentImport.svelte

A modal dialog for importing components from CSV files:

- File upload with drag and drop support
- Progress indication
- Success/error feedback
- Preview of imported components

## Usage

Import the ComponentManager into your main App.svelte file to use the complete Component Management UI:

```svelte
<script>
  import ComponentManager from './components/ComponentManager.svelte';
</script>

<main>
  <ComponentManager />
</main>
```

Or use individual components as needed:

```svelte
<script>
  import ComponentList from './components/ComponentList.svelte';
</script>

<main>
  <ComponentList />
</main>
```

## Styling

The UI uses Tailwind CSS for styling with a custom color scheme defined in app.css:

- Primary color: #2d6cdf (blue)
- Secondary color: #50a38e (teal)
- Background color: #f7f9fb (light gray)
- Text colors: #1a1a1a (main) and #6b7280 (muted)

The design follows modern UI principles with:

- Card-based layouts for component display
- Clean, readable typography
- Appropriate spacing and padding
- Subtle shadows and borders
- Color-coded badges for safety levels and trust zones
- Responsive design that works on all screen sizes

## Icons

The UI uses Lucide icons for a consistent and professional look:

- Shield: for security-related items
- Settings: for ECUs and configuration
- AlertTriangle: for sensors and warnings
- Database: for data storage
- Plus/Edit/Delete: for CRUD operations

## API Integration

The UI connects to the backend API through the API client functions in the `/api` directory:

- componentApi.getAll(): Fetch all components
- componentApi.getById(): Fetch a specific component
- componentApi.create(): Create a new component
- componentApi.update(): Update an existing component
- componentApi.delete(): Delete a component
- componentApi.importFromCsv(): Import components from CSV
- componentApi.getExportUrl(): Get URL for CSV export

## Error Handling

The UI includes comprehensive error handling:

- Loading states with spinners
- Error messages for failed API calls
- Validation feedback in forms
- Confirmation dialogs for destructive actions

## Accessibility

The UI follows accessibility best practices:

- Proper semantic HTML elements
- ARIA attributes where needed
- Keyboard navigation support
- Color contrast that meets WCAG standards
- Focus management for modals and forms

## Future Enhancements

Planned enhancements to the Component Management UI include:

- Component relationship visualization
- Batch operations for multiple components
- Advanced filtering and sorting options
- Component templates for quick creation
- Interactive component editor with drag-and-drop connections
