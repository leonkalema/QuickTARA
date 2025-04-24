# Component Management

The Component Management module provides a comprehensive interface for managing automotive components within QuickTARA.

## Features

- **Component Listing**: View all components in a responsive card-based layout
- **Component Creation**: Add new components with detailed specifications
- **Component Editing**: Modify existing component details
- **Component Deletion**: Remove components from the system
- **CSV Import/Export**: Bulk import and export components in CSV format
- **Filtering & Search**: Find components by type, safety level, trust zone, or search term

## Architecture

The Component Management UI follows a modular architecture with clear separation of concerns:

1. **ComponentManager.svelte**: Main container for component management features
2. **ComponentList.svelte**: Handles component listing, filtering, and CRUD operations
3. **ComponentCard.svelte**: Individual component display card with actions
4. **ComponentForm.svelte**: Form for adding and editing components
5. **ComponentFilter.svelte**: Advanced filtering interface
6. **ComponentImport.svelte**: CSV import functionality

## API Integration

The UI connects with the backend using the Component API client (`/frontend/src/api/components.ts`), which provides methods for:

- Fetching all components
- Getting a component by ID
- Creating new components
- Updating existing components
- Deleting components
- Importing components from CSV
- Exporting components to CSV

## Data Validation

Component data is validated at multiple levels:

1. **Client-side validation**: Ensures all required fields are provided and formatted correctly
2. **API validation**: Backend validation ensures data integrity and consistency
3. **Database constraints**: Enforces data relationships and uniqueness

## Usage

### Adding a Component

1. Click the "Add Component" button
2. Fill in the component details in the form:
   - Component ID (must be unique, alphanumeric, hyphens and underscores allowed)
   - Name (required)
   - Type (ECU, Sensor, Gateway, etc.)
   - Safety Level (ASIL A-D, QM)
   - Location (Internal/External)
   - Trust Zone (Critical, Boundary, Standard, Untrusted)
   - Interfaces (communication protocols used by the component)
   - Access Points (physical or debug interfaces)
   - Data Types (types of data handled by the component)
   - Connected Components (other components this component is connected to)
3. Click "Save Component" to create the component

### Importing Components

1. Click the "Import" button
2. Select a CSV file or drag and drop it into the designated area
3. Click "Import Components" to process the file
4. View the import results, including any errors

### Filtering Components

1. Use the search box to filter by component ID or name
2. Use the type dropdown to filter by component type
3. Use the safety level dropdown to filter by ASIL rating
4. Use the trust zone dropdown to filter by security domain

## Component Properties

| Property      | Description                                      | Example Values                  |
|---------------|--------------------------------------------------|--------------------------------|
| component_id  | Unique identifier                                | ECU001, SNS001                 |
| name          | Human-readable name                              | Engine Control Unit            |
| type          | Component type                                   | ECU, Sensor, Gateway           |
| safety_level  | Automotive Safety Integrity Level                | ASIL D, ASIL C, QM             |
| interfaces    | Communication protocols                          | CAN, FlexRay, Ethernet         |
| access_points | Physical/debug interfaces                        | OBD-II, Debug Port             |
| data_types    | Nature of data handled                           | Control Commands, Sensor Data  |
| location      | Physical placement                               | Internal, External             |
| trust_zone    | Security domain                                  | Critical, Boundary, Untrusted  |
| connected_to  | Connected component IDs                          | ECU002, SNS001                 |

## CSV Import Format

The CSV import format must include the following headers:

```csv
component_id,name,type,safety_level,interfaces,access_points,data_types,location,trust_zone,connected_to
```

Multiple values in a single field should be separated by the pipe character:

```csv
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003
```

## Error Handling

The UI handles various error scenarios gracefully:

- Network errors when communicating with the API
- Validation errors in form submissions
- Import errors for invalid CSV files
- Duplicate component IDs

Error messages are displayed in context to help users quickly resolve issues.
