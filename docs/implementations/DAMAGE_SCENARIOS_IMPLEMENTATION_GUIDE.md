# Damage Scenarios Implementation Guide

## Overview

Damage Scenarios represent the third phase in the QuickTARA workflow, following Item Definition (Scope) and Asset Identification (Components). This phase focuses on identifying potential negative outcomes that could result from security property violations of the identified assets.

According to ISO/SAE 21434 and UNECE R155, damage scenarios describe what could happen if the security properties (CIA triad, authenticity, authorization, non-repudiation) of assets are compromised. These scenarios form the foundation for subsequent impact analysis and threat modeling.

## Key Concept: Impact Propagation Engine

The cornerstone of our Damage Scenarios implementation is the **Impact Propagation Engine** - an intelligent system that leverages existing asset information to semi-automate the creation of damage scenarios.

This approach builds upon the work already completed in the Asset Identification phase, where we've established:

1. **Component CIA Properties**: Security properties defined for each component
2. **Component Connectivity**: Relationships between components
3. **Trust Boundaries**: Components within trust zones
4. **Scope Definition**: System boundaries and context

The Impact Propagation Engine analyzes this information to:

- Trace how security impacts propagate through connected components
- Identify all affected components based on an initial compromise
- Suggest appropriate damage categories and impact types
- Generate meaningful damage scenario descriptions

## Implementation Requirements

### Database Schema

### Database Schema

#### Enums for Validation

```python
class DamageCategory(str, Enum):
    """Categories of damage scenarios"""
    DATA_BREACH = "Data Breach"
    SERVICE_DISRUPTION = "Service Disruption"
    VEHICLE_CONTROL = "Vehicle Control"
    PRIVACY_VIOLATION = "Privacy Violation"
    FINANCIAL_LOSS = "Financial Loss"
    SAFETY_HAZARD = "Safety Hazard"
    REPUTATION_DAMAGE = "Reputation Damage"


class SecurityProperty(str, Enum):
    """Security properties that can be violated"""
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"
    AUTHENTICITY = "authenticity"
    AUTHORIZATION = "authorization"
    NON_REPUDIATION = "non-repudiation"
```

#### DamageScenario Model (SQLAlchemy)

```python
class DamageScenario(Base):
    __tablename__ = "damage_scenarios"
    
    # Primary Key
    scenario_id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    scope_id = Column(String, ForeignKey("scopes.scope_id"), nullable=False)
    
    # Security Properties being violated
    violated_properties = Column(ARRAY(String), nullable=False)  # List of security properties being violated
    
    # Categorization
    category = Column(String, nullable=False)  # e.g., "Data Breach", "Service Disruption", "Vehicle Control"
    
    # Damage Types (multiple can apply)
    safety_impact = Column(Boolean, default=False)
    financial_impact = Column(Boolean, default=False)
    operational_impact = Column(Boolean, default=False)
    privacy_impact = Column(Boolean, default=False)
    
    # Versioning & Traceability
    version = Column(Integer, default=1, nullable=False)
    revision_notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)  # For soft delete
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scope = relationship("Scope", back_populates="damage_scenarios")
    threat_scenarios = relationship("ThreatScenario", back_populates="damage_scenario")
    
    # Many-to-many relationship with components
    affected_components = relationship(
        "Component",
        secondary=component_damage_scenario,
        back_populates="damage_scenarios"
    )
```

#### Pydantic Models for Validation

```python
class DamageScenarioBase(BaseModel):
    """Base Damage Scenario attributes"""
    name: str = Field(..., description="Name of the damage scenario")
    description: str = Field(..., min_length=10, description="Detailed description of what could happen")
    scope_id: str = Field(..., description="Associated system scope ID")
    affected_component_ids: List[str] = Field(..., min_items=1, description="List of affected component IDs")
    violated_properties: List[SecurityProperty] = Field(..., min_items=1, description="Security properties being violated")
    category: DamageCategory = Field(..., description="Category of damage")
    safety_impact: bool = Field(default=False, description="Impact on safety")
    financial_impact: bool = Field(default=False, description="Impact on finances")
    operational_impact: bool = Field(default=False, description="Impact on operations")
    privacy_impact: bool = Field(default=False, description="Impact on privacy")
    revision_notes: Optional[str] = Field(None, description="Notes about this revision")
    
    @validator('violated_properties')
    def validate_violated_properties(cls, v):
        if not v:
            raise ValueError('At least one violated security property must be specified')
        return v
    
    @validator('safety_impact', 'financial_impact', 'operational_impact', 'privacy_impact')
    def validate_impact_types(cls, v, values):
        # Ensure at least one impact type is selected
        if 'safety_impact' in values and not (values['safety_impact'] or 
                                             values.get('financial_impact', False) or 
                                             values.get('operational_impact', False) or 
                                             values.get('privacy_impact', False)):
            if not v:  # If this is also False
                raise ValueError('At least one impact type must be selected')
        return v


class DamageScenarioCreate(DamageScenarioBase):
    """Used for creating a new damage scenario"""
    scenario_id: Optional[str] = Field(None, description="Optional unique scenario identifier")


class DamageScenarioUpdate(BaseModel):
    """Used for updating an existing damage scenario"""
    name: Optional[str] = None
    description: Optional[str] = None
    scope_id: Optional[str] = None
    affected_component_ids: Optional[List[str]] = None
    violated_properties: Optional[List[SecurityProperty]] = None
    category: Optional[DamageCategory] = None
    safety_impact: Optional[bool] = None
    financial_impact: Optional[bool] = None
    operational_impact: Optional[bool] = None
    privacy_impact: Optional[bool] = None
    revision_notes: Optional[str] = Field(..., description="Notes about this revision")
    
    @validator('affected_component_ids')
    def validate_affected_component_ids(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('If specified, affected_component_ids cannot be empty')
        return v
    
    @validator('violated_properties')
    def validate_violated_properties(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('If specified, violated_properties cannot be empty')
        return v


class DamageScenario(DamageScenarioBase):
    """Full damage scenario model with ID and timestamps"""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    version: int = Field(..., description="Version number of this scenario")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DamageScenarioList(BaseModel):
    """List of damage scenarios"""
    scenarios: List[DamageScenario]
    total: int
```
```

#### Updates to Existing Models

```python
# Association table for many-to-many relationship between components and damage scenarios
component_damage_scenario = Table(
    "component_damage_scenario",
    Base.metadata,
    Column("component_id", String, ForeignKey("components.component_id")),
    Column("scenario_id", String, ForeignKey("damage_scenarios.scenario_id")),
    UniqueConstraint("component_id", "scenario_id", name="uq_component_damage_scenario")
)

# Update to Component model to establish relationship with damage scenarios
class Component(Base):
    # Existing fields...
    # Many-to-many relationship with damage scenarios
    damage_scenarios = relationship(
        "DamageScenario",
        secondary=component_damage_scenario,
        back_populates="affected_components"
    )
    
# Update to Scope model
class Scope(Base):
    # Existing fields...
    # One-to-many relationship with damage scenarios
    damage_scenarios = relationship("DamageScenario", back_populates="scope")
```

### API Endpoints

#### Damage Scenarios API

1. **Create Damage Scenario**
   - Endpoint: `POST /api/damage-scenarios`
   - Request Body:
     ```json
     {
       "name": "Vehicle Immobilization",
       "description": "Unauthorized access to the vehicle's immobilizer system could prevent the vehicle from starting or cause it to shut down while in operation.",
       "scope_id": "SCOPE-001",
       "affected_component_ids": ["COMP-001", "COMP-002"],
       "violated_properties": ["integrity", "availability"],
       "category": "Vehicle Control",
       "safety_impact": true,
       "financial_impact": true,
       "operational_impact": true,
       "privacy_impact": false,
       "revision_notes": "Initial creation"
     }
     ```
   - Response: Created damage scenario object

2. **Get All Damage Scenarios**
   - Endpoint: `GET /api/damage-scenarios`
   - Query Parameters:
     - `scope_id` (optional): Filter by scope
     - `component_id` (optional): Filter by affected component
     - `category` (optional): Filter by category
     - `violated_property` (optional): Filter by violated security property
     - `impact_type` (optional): Filter by impact type (safety, financial, etc.)
   - Response: List of damage scenarios

3. **Get Damage Scenario by ID**
   - Endpoint: `GET /api/damage-scenarios/{scenario_id}`
   - Response: Damage scenario object

4. **Update Damage Scenario**
   - Endpoint: `PUT /api/damage-scenarios/{scenario_id}`
   - Request Body: Same as create with updated fields, plus required revision_notes
   - Response: Updated damage scenario object with incremented version

5. **Delete Damage Scenario**
   - Endpoint: `DELETE /api/damage-scenarios/{scenario_id}`
   - Response: Success message

6. **Get Damage Scenarios by Scope**
   - Endpoint: `GET /api/scopes/{scope_id}/damage-scenarios`
   - Response: List of damage scenarios for the specified scope

7. **Get Damage Scenarios by Component**
   - Endpoint: `GET /api/components/{component_id}/damage-scenarios`
   - Response: List of damage scenarios affecting the specified component

#### Impact Propagation Engine API

1. **Generate Impact Propagation**
   - Endpoint: `POST /api/damage-scenarios/propagate-impact`
   - Request Body:
     ```json
     {
       "scope_id": "SCOPE-001",
       "initial_component_id": "COMP-001",
       "impact_type": "integrity"
     }
     ```
   - Response:
     ```json
     {
       "affected_component_ids": ["COMP-001", "COMP-002", "COMP-003"],
       "violated_properties": ["integrity", "availability"],
       "suggested_category": "Vehicle Control",
       "suggested_impacts": {
         "safety": true,
         "financial": true,
         "operational": true,
         "privacy": false
       },
       "suggested_name": "Vehicle Control System Compromise",
       "suggested_description": "Unauthorized modification of the vehicle control system could lead to unexpected vehicle behavior, potentially affecting steering, braking, or acceleration.",
       "propagation_paths": [
         {
           "source": "COMP-001",
           "target": "COMP-002",
           "rule_applied": "High integrity components propagate integrity impacts"
         },
         {
           "source": "COMP-002",
           "target": "COMP-003",
           "rule_applied": "Components in same trust zone propagate impacts"
         }
       ]
     }
     ```

2. **Get Components by Scope with Propagation Data**
   - Endpoint: `GET /api/scopes/{scope_id}/components-with-propagation`
   - Response: List of components with their connectivity and security properties for visualization

3. **Get Propagation Rules**
   - Endpoint: `GET /api/damage-scenarios/propagation-rules`
   - Response: List of available propagation rules and their descriptions

4. **Get Suggested Damage Categories**
   - Endpoint: `GET /api/damage-scenarios/suggested-categories`
   - Query Parameters:
     - `component_types` (optional): Filter by component types
     - `violated_properties` (optional): Filter by violated security properties
   - Response: List of suggested damage categories with descriptions

### Frontend Components

The frontend implementation consists of several key components that work together to provide a complete damage scenario management interface. These components are integrated into the Analysis section of the application as a new tab.

#### API Client (damage-scenarios.ts)

The API client provides type-safe access to the damage scenarios backend API:

```typescript
// Key interfaces and enums
export enum DamageCategory {
  PHYSICAL = "Physical",
  OPERATIONAL = "Operational",
  FINANCIAL = "Financial",
  PRIVACY = "Privacy",
  SAFETY = "Safety",
  ENVIRONMENTAL = "Environmental",
  REPUTATIONAL = "Reputational",
  LEGAL = "Legal",
  OTHER = "Other"
}

export enum ImpactType {
  DIRECT = "Direct",
  INDIRECT = "Indirect",
  CASCADING = "Cascading"
}

export enum SeverityLevel {
  LOW = "Low",
  MEDIUM = "Medium",
  HIGH = "High",
  CRITICAL = "Critical"
}

export interface DamageScenario {
  scenario_id: string;
  name: string;
  description: string;
  damage_category: DamageCategory;
  impact_type: ImpactType;
  confidentiality_impact: boolean;
  integrity_impact: boolean;
  availability_impact: boolean;
  severity: SeverityLevel;
  impact_details?: Record<string, any>;
  scope_id: string;
  primary_component_id: string;
  affected_component_ids: string[];
  version: number;
  revision_notes?: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

// API service methods
export const damageScenarioApi = {
  async getAll(options?: {...}): Promise<DamageScenarioList> {...},
  async getById(id: string): Promise<DamageScenario> {...},
  async create(scenario: DamageScenarioCreate): Promise<DamageScenario> {...},
  async update(id: string, scenario: DamageScenarioUpdate): Promise<DamageScenario> {...},
  async delete(id: string): Promise<void> {...},
  async getPropagationSuggestions(componentId: string, impacts: {...}): Promise<PropagationSuggestionResponse> {...}
}
```

#### DamageScenarioManager.svelte

Main container component that manages the overall damage scenario workflow:

```svelte
<script lang="ts">
  // Imports and state management
  import { onMount } from 'svelte';
  import { damageScenarioApi, type DamageScenario } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import { showSuccess, showError } from '../ToastManager.svelte';
  
  // State variables
  let scenarios: DamageScenario[] = [];
  let totalScenarios: number = 0;
  let isLoading = true;
  let showForm = false;
  let editingScenario: DamageScenario | null = null;
  
  // Stats tracking
  let stats = {
    totalScenarios: 0,
    criticalScenarios: 0,
    highScenarios: 0,
    directImpacts: 0,
    cascadingImpacts: 0
  };
  
  // Load scenarios on component mount
  onMount(async () => {
    await loadDamageScenarios();
  });
  
  // CRUD operations for damage scenarios
  async function loadDamageScenarios() { /* ... */ }
  function handleCreateScenario() { /* ... */ }
  async function handleFormSubmit(event: CustomEvent) { /* ... */ }
  async function handleDeleteScenario(scenario: DamageScenario) { /* ... */ }
</script>

<!-- UI Template -->
<div class="space-y-6">
  <!-- Stats cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
    <!-- Various metric cards for statistics -->
  </div>
  
  <!-- Action bar with buttons -->
  <div class="flex justify-between items-center mb-6">...</div>
  
  <!-- Filters section -->
  <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">...</div>
  
  <!-- Damage Scenario List component -->
  <DamageScenarioListComponent 
    scenarios={scenarios}
    totalScenarios={totalScenarios}
    currentPage={currentPage}
    pageSize={pageSize}
    isLoading={isLoading}
    error={error}
    on:edit={(e: CustomEvent<DamageScenario>) => handleEditScenario(e.detail)}
    on:delete={(e: CustomEvent<DamageScenario>) => handleDeleteScenario(e.detail)}
    on:pageChange={(e: CustomEvent<number>) => handlePageChange(e.detail)}
  />
  
  <!-- Damage Scenario Form Dialog -->
  {#if showForm}
    <div class="fixed inset-0 backdrop-blur-sm bg-neutral-900/40 flex items-center justify-center z-50 p-4">
      <DamageScenarioForm
        scenario={editingScenario}
        scopeId={selectedScopeId || undefined}
        componentId={selectedComponentId || undefined}
        on:submit={handleFormSubmit}
        on:cancel={handleFormCancel}
      />
    </div>
  {/if}
</div>
```

The DamageScenarioManager serves as the main container for the damage scenarios functionality. It handles:

- Loading and displaying damage scenarios with filtering and pagination
- Creating, editing, and deleting damage scenarios
- Displaying statistics about the scenarios (counts by severity and impact type)
- Managing the state of the form dialog for creating/editing scenarios

#### DamageScenarioList.svelte

Component for displaying the list of damage scenarios with pagination and actions:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { RefreshCw, AlertTriangle, Shield, Activity, Edit, Trash2, Eye } from '@lucide/svelte';
  import type { DamageScenario } from '../../api/damage-scenarios';
  
  // Props
  export let scenarios: DamageScenario[] = [];
  export let totalScenarios: number = 0;
  export let currentPage: number = 1;
  export let pageSize: number = 10;
  export let isLoading: boolean = false;
  export let error: string = '';
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Computed properties
  $: totalPages = Math.ceil(totalScenarios / pageSize);
  $: startItem = (currentPage - 1) * pageSize + 1;
  $: endItem = Math.min(startItem + pageSize - 1, totalScenarios);
  
  // Helper functions
  function getSeverityColor(severity: string): string { /* ... */ }
  function getImpactTypeColor(impactType: string): string { /* ... */ }
  function formatDate(dateString: string): string { /* ... */ }
</script>

<!-- UI Template -->
<div>
  {#if isLoading}
    <!-- Loading state -->
  {:else if error}
    <!-- Error state -->
  {:else if scenarios.length === 0}
    <!-- Empty state -->
  {:else}
    <!-- Data table with scenarios -->
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Table header -->
        <thead>...</thead>
        
        <!-- Table body -->
        <tbody>
          {#each scenarios as scenario}
            <tr class="hover:bg-gray-50">
              <!-- Scenario details columns -->
              <td>...</td>
              
              <!-- Action buttons -->
              <td>
                <div class="flex space-x-2">
                  <button on:click={() => dispatch('view', scenario)}>...</button>
                  <button on:click={() => dispatch('edit', scenario)}>...</button>
                  <button on:click={() => dispatch('delete', scenario)}>...</button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      
      <!-- Pagination controls -->
      {#if totalPages > 1}
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
          <!-- Pagination UI -->
        </div>
      {/if}
    </div>
  {/if}
</div>
```

The DamageScenarioList component is responsible for:

- Displaying damage scenarios in a tabular format
- Showing appropriate loading, error, and empty states
- Providing action buttons for viewing, editing, and deleting scenarios
- Implementing pagination controls for navigating through large sets of scenarios
- Visual indicators for severity and impact types

#### DamageScenarioForm.svelte

Component for creating and editing damage scenarios:

```svelte
<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, AlertTriangle, Save, Trash2, Loader2 } from '@lucide/svelte';
  import { 
    damageScenarioApi, 
    type DamageScenario, 
    type DamageScenarioCreate,
    type PropagationSuggestion,
    DamageCategory,
    ImpactType,
    SeverityLevel
  } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  
  // Props
  export let scenario: DamageScenario | null = null;
  export let scopeId: string | undefined = undefined;
  export let componentId: string | undefined = undefined;
  
  // State
  let isLoading = false;
  let isSaving = false;
  let isPropagationLoading = false;
  let formData: DamageScenarioCreate;
  let propagationSuggestions: PropagationSuggestion[] = [];
  let scopes: Array<{ id: string, name: string }> = [];
  let components: Array<{ id: string, name: string }> = [];
  let showPropagationSuggestions = false;
  let formErrors: Record<string, string> = {};
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Initialize form data and load dependencies
  onMount(async () => {
    isLoading = true;
    
    try {
      // Initialize form data
      initFormData();
      
      // Load scopes and components in parallel
      const [scopesResult, componentsResult] = await Promise.all([
        safeApiCall(() => fetch('/api/scopes').then(res => res.json())),
        safeApiCall(() => fetch('/api/components').then(res => res.json()))
      ]);
      
      // Process results and load propagation suggestions if needed
      // ...
    } catch (err) {
      console.error('Error initializing form:', err);
    } finally {
      isLoading = false;
    }
  });
  
  // Load propagation suggestions based on selected component and CIA impacts
  async function loadPropagationSuggestions() { /* ... */ }
  
  // Form validation and submission
  function validateForm(): boolean { /* ... */ }
  async function handleSubmit() { /* ... */ }
  
  // Handle component selection and propagation suggestions
  function handlePrimaryComponentChange() { /* ... */ }
  function handleCIAChange() { /* ... */ }
  function handleApplySuggestions() { /* ... */ }
</script>

<div class="bg-white rounded-lg shadow-lg overflow-hidden max-w-3xl mx-auto">
  <!-- Form header -->
  <div class="flex justify-between items-center px-6 py-4 bg-gray-50 border-b border-gray-200">...</div>
  
  {#if isLoading}
    <!-- Loading state -->
  {:else}
    <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
      <!-- Basic Information section -->
      <div class="space-y-4">...</div>
      
      <!-- Impact Details section -->
      <div class="space-y-4">...</div>
      
      <!-- Component Selection section -->
      <div class="space-y-4">
        <!-- Primary Component selection -->
        <div>...</div>
        
        <!-- Propagation Suggestions -->
        {#if formData.primary_component_id}
          <div class="bg-gray-50 p-4 rounded-md border border-gray-200">
            <!-- Propagation UI with suggestions based on component connections -->
            <!-- Shows potential affected components based on the selected primary component -->
          </div>
        {/if}
        
        <!-- Affected Components selection -->
        <div>...</div>
      </div>
      
      <!-- Form actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">...</div>
    </form>
  {/if}
</div>
```

The DamageScenarioForm component provides a comprehensive interface for creating and editing damage scenarios with the following features:

- Form fields for all damage scenario properties (name, description, category, etc.)
- CIA impact selection with validation to ensure at least one impact is selected
- Component selection with primary and affected components
- Integration with the Impact Propagation Engine to suggest affected components
- Form validation with error messages
- Loading and saving states with appropriate UI feedback

#### Integration with AnalysisManager

The Damage Scenarios module is integrated into the existing AnalysisManager component as a new tab:

```svelte
<!-- In AnalysisManager.svelte -->
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
  
  // Active tab management
  let activeTab = 'general-analysis'; // 'general-analysis', 'threat-analysis', 'vulnerability-analysis', 'damage-scenarios'
  // ...
</script>

<div class="space-y-6">
  <!-- Tab Navigation -->
  <div class="border-b border-gray-200">
    <nav class="-mb-px flex space-x-8" aria-label="Analysis sections">
      <!-- Existing tabs -->
      
      <!-- Damage Scenarios Tab -->
      <button
        class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'damage-scenarios' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
        on:click={() => activeTab = 'damage-scenarios'}
      >
        <Zap class="h-5 w-5" />
        <span>Damage Scenarios</span>
      </button>
    </nav>
  </div>

  <!-- Tab Content -->
  <!-- Existing tab content -->
  
  <!-- Damage Scenarios Tab Content -->
  {#if activeTab === 'damage-scenarios'}
    <DamageScenarioManager />
  {/if}
</div>
```

This integration allows users to seamlessly switch between different analysis activities while maintaining a consistent user interface and navigation pattern.
  import DamageScenarioStats from './DamageScenarioStats.svelte';
  import DamageScenarioFilter from './DamageScenarioFilter.svelte';
  import { damageScenarioApi } from '../api/api';
  import type { DamageScenario } from '../types';
  
  // State management
  let damageScenarios: DamageScenario[] = [];
  let filteredScenarios: DamageScenario[] = [];
  let isLoading = true;
  let error = '';
  
  // Filter state
  let filters = {
    category: '',
    safetyImpact: false,
    financialImpact: false,
    operationalImpact: false,
    privacyImpact: false,
    securityProperty: '',
    componentId: ''
  };
  
  onMount(async () => {
    await loadDamageScenarios();
  });
  
  async function loadDamageScenarios() {
    isLoading = true;
    error = '';
    
    try {
      damageScenarios = await damageScenarioApi.getAll();
      applyFilters();
    } catch (err) {
      error = 'Failed to load damage scenarios';
      console.error(err);
    } finally {
      isLoading = false;
    }
  }
  
  function applyFilters() {
    // Implementation of filtering logic
  }
</script>

<div class="damage-scenario-manager">
  <DamageScenarioStats scenarios={filteredScenarios} />
  <DamageScenarioFilter bind:filters={filters} on:filter={applyFilters} />
  <DamageScenarioList 
    scenarios={filteredScenarios} 
    on:delete={handleDelete}
    on:edit={handleEdit}
    on:view={handleView}
  />
</div>
```

#### DamageScenarioList.svelte

Component to display the list of damage scenarios with options to view, edit, or delete:

```svelte
<script lang="ts">
  import DamageScenarioCard from './DamageScenarioCard.svelte';
  import { createEventDispatcher } from 'svelte';
  import type { DamageScenario } from '../types';
  
  export let scenarios: DamageScenario[] = [];
  
  const dispatch = createEventDispatcher();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each scenarios as scenario (scenario.scenario_id)}
    <DamageScenarioCard 
      {scenario}
      on:view={() => dispatch('view', scenario)}
      on:edit={() => dispatch('edit', scenario)}
      on:delete={() => dispatch('delete', scenario.scenario_id)}
    />
  {/each}
</div>
```

#### DamageScenarioForm.svelte

Smart form component with Impact Propagation Engine integration:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { componentApi, scopeApi, damageScenarioApi } from '../api/api';
  import { showSuccess, showError, showInfo } from '../components/ToastManager.svelte';
  import { Zap, AlertTriangle, Info, CheckCircle2, RefreshCw } from '@lucide/svelte';
  import type { DamageScenario, Component, Scope, ImpactPropagation } from '../types';
  import { DamageCategory, SecurityProperty, ImpactType } from '../types/enums';
  
  export let scenario: Partial<DamageScenario> = {
    name: '',
    description: '',
    scope_id: '',
    affected_component_ids: [],
    violated_properties: [],
    category: undefined,
    safety_impact: false,
    financial_impact: false,
    operational_impact: false,
    privacy_impact: false,
    revision_notes: editMode ? 'Updated scenario' : 'Initial creation'
  };
  
  export let editMode = false;
  export let viewMode = false;
  
  // Component state
  let availableComponents: Component[] = [];
  let availableScopes: Scope[] = [];
  let scopeComponents: Component[] = [];
  let errors: Record<string, string> = {};
  let isSubmitting = false;
  let isGeneratingSuggestions = false;
  let showPropagationPanel = false;
  
  // Impact propagation state
  let selectedInitialComponent: string = '';
  let selectedImpactType: ImpactType = ImpactType.INTEGRITY;
  let propagationResult: ImpactPropagation | null = null;
  
  // Form validation
  function validateForm(): boolean {
    errors = {};
    
    // Required fields
    if (!scenario.name?.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!scenario.description?.trim()) {
      errors.description = 'Description is required';
    } else if (scenario.description.length < 10) {
      errors.description = 'Description must be at least 10 characters';
    }
    
    if (!scenario.scope_id) {
      errors.scope_id = 'System scope is required';
    }
    
    if (!scenario.category) {
      errors.category = 'Category is required';
    }
    
    // Affected components validation
    if (!scenario.affected_component_ids || scenario.affected_component_ids.length === 0) {
      errors.affected_component_ids = 'At least one affected component must be selected';
    }
    
    // Violated properties validation
    if (!scenario.violated_properties || scenario.violated_properties.length === 0) {
      errors.violated_properties = 'At least one violated security property must be selected';
    }
    
    // Impact types validation
    if (!scenario.safety_impact && !scenario.financial_impact && 
        !scenario.operational_impact && !scenario.privacy_impact) {
      errors.impact_types = 'At least one impact type must be selected';
    }
    
    // Revision notes required for updates
    if (editMode && !scenario.revision_notes?.trim()) {
      errors.revision_notes = 'Please provide notes about this revision';
    }
    
    return Object.keys(errors).length === 0;
  }
  
  async function handleSubmit() {
    if (!validateForm()) {
      // Scroll to the first error
      const firstErrorId = Object.keys(errors)[0];
      document.getElementById(firstErrorId)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    
    isSubmitting = true;
    dispatch('submit', scenario);
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
  
  // Load available components and scopes for selection
  async function loadData() {
    try {
      [availableComponents, availableScopes] = await Promise.all([
        componentApi.getAll(),
        scopeApi.getAll()
      ]);
    } catch (err) {
      console.error('Failed to load data', err);
      showError('Failed to load components or scopes');
    }
  }
  
  // Filter components by selected scope
  async function loadScopeComponents(scopeId: string) {
    if (!scopeId) {
      scopeComponents = [];
      return;
    }
    
    try {
      scopeComponents = await componentApi.getByScopeId(scopeId);
    } catch (err) {
      console.error('Failed to load scope components', err);
      showError('Failed to load components for the selected scope');
    }
  }
  
  // Generate impact propagation suggestions
  async function generatePropagationSuggestions() {
    if (!selectedInitialComponent || !selectedImpactType || !scenario.scope_id) {
      showError('Please select a scope, initial component, and impact type');
      return;
    }
    
    isGeneratingSuggestions = true;
    
    try {
      propagationResult = await damageScenarioApi.generateImpactPropagation(
        scenario.scope_id,
        selectedInitialComponent,
        selectedImpactType
      );
      
      // Apply suggestions to the form
      if (propagationResult) {
        scenario.affected_component_ids = propagationResult.affected_component_ids;
        scenario.violated_properties = propagationResult.violated_properties;
        scenario.category = propagationResult.suggested_category;
        scenario.safety_impact = propagationResult.suggested_impacts.safety;
        scenario.financial_impact = propagationResult.suggested_impacts.financial;
        scenario.operational_impact = propagationResult.suggested_impacts.operational;
        scenario.privacy_impact = propagationResult.suggested_impacts.privacy;
        
        // Generate a name suggestion if empty
        if (!scenario.name) {
          scenario.name = propagationResult.suggested_name;
        }
        
        // Generate a description suggestion if empty
        if (!scenario.description) {
          scenario.description = propagationResult.suggested_description;
        }
        
        showSuccess('Suggestions applied based on impact propagation analysis');
      }
    } catch (err) {
      console.error('Failed to generate impact propagation', err);
      showError('Failed to generate impact propagation suggestions');
    } finally {
      isGeneratingSuggestions = false;
    }
  }
  
  // Watch for scope changes to load relevant components
  $: if (scenario.scope_id) {
    loadScopeComponents(scenario.scope_id);
  }
  
  $: if (!viewMode) {
    loadData();
  }
  
  const dispatch = createEventDispatcher();
</script>

<div class="bg-white rounded-xl shadow-lg p-6 max-w-2xl mx-auto border border-gray-100 {viewMode ? 'view-mode' : ''}">
  <form on:submit|preventDefault={handleSubmit}>
    <div class="mb-6 pb-4 border-b border-gray-200 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900">
        {#if viewMode}
          Damage Scenario Details
        {:else if editMode}
          Edit Damage Scenario
        {:else}
          Create New Damage Scenario
        {/if}
      </h2>
      
      {#if !viewMode}
        <div class="text-sm text-gray-500">
          * Required fields
        </div>
      {/if}
    </div>
    
    <!-- Impact Propagation Engine Panel -->
    {#if !viewMode && !editMode}
      <div class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div class="flex items-center mb-3">
          <Zap size={20} class="text-blue-600 mr-2" />
          <h3 class="text-lg font-medium text-blue-800">Impact Propagation Engine</h3>
          <button 
            type="button" 
            class="ml-auto text-blue-600 hover:text-blue-800 text-sm flex items-center"
            on:click={() => showPropagationPanel = !showPropagationPanel}
          >
            {showPropagationPanel ? 'Hide' : 'Show'} Options
          </button>
        </div>
        
        {#if showPropagationPanel}
          <div class="mb-4">
            <p class="text-sm text-blue-700 mb-3">
              Select a scope, initial component, and impact type to generate damage scenario suggestions.
            </p>
            
            <!-- Scope Selection -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div class="form-group">
                <label for="scope_id" class="form-label">System Scope *</label>
                <select 
                  id="scope_id" 
                  class="form-select" 
                  bind:value={scenario.scope_id} 
                  disabled={viewMode}
                >
                  <option value="" disabled selected>Select a system scope</option>
                  {#each availableScopes as scope}
                    <option value={scope.scope_id}>{scope.name}</option>
                  {/each}
                </select>
              </div>
              
              <!-- Initial Component Selection -->
              <div class="form-group">
                <label for="initial_component" class="form-label">Initial Component *</label>
                <select 
                  id="initial_component" 
                  class="form-select" 
                  bind:value={selectedInitialComponent}
                  disabled={!scenario.scope_id || scopeComponents.length === 0}
                >
                  <option value="" disabled selected>Select initial component</option>
                  {#each scopeComponents as component}
                    <option value={component.component_id}>{component.name}</option>
                  {/each}
                </select>
                {#if !scenario.scope_id}
                  <p class="text-sm text-blue-600 mt-1">Please select a scope first</p>
                {/if}
              </div>
            </div>
            
            <!-- Impact Type Selection -->
            <div class="mb-4">
              <label class="form-label block mb-2">Impact Type *</label>
              <div class="flex flex-wrap gap-3">
                {#each Object.entries(ImpactType) as [key, value]}
                  <label class="inline-flex items-center">
                    <input 
                      type="radio" 
                      name="impactType" 
                      value={value} 
                      checked={selectedImpactType === value}
                      on:change={() => selectedImpactType = value}
                      class="form-radio"
                    />
                    <span class="ml-2">{value}</span>
                  </label>
                {/each}
              </div>
            </div>
            
            <!-- Generate Button -->
            <div class="flex justify-end">
              <button 
                type="button" 
                class="btn btn-primary flex items-center gap-2" 
                disabled={!scenario.scope_id || !selectedInitialComponent || isGeneratingSuggestions}
                on:click={generatePropagationSuggestions}
              >
                {#if isGeneratingSuggestions}
                  <RefreshCw size={16} class="animate-spin" />
                  Generating...
                {:else}
                  <Zap size={16} />
                  Generate Suggestions
                {/if}
              </button>
            </div>
          </div>
        {:else}
          <p class="text-sm text-blue-700">
            Use the Impact Propagation Engine to automatically suggest affected components, 
            security properties, and impact categories based on your system architecture.
          </p>
        {/if}
        
        <!-- Propagation Results Preview -->
        {#if propagationResult && !isGeneratingSuggestions}
          <div class="mt-3 pt-3 border-t border-blue-200">
            <div class="flex items-center mb-2">
              <CheckCircle2 size={16} class="text-green-600 mr-2" />
              <h4 class="text-sm font-medium text-blue-800">Propagation Results</h4>
            </div>
            <p class="text-xs text-blue-700 mb-2">
              Impact propagates to {propagationResult.affected_component_ids.length} components 
              with {propagationResult.violated_properties.length} security properties affected.
            </p>
            <div class="flex flex-wrap gap-1 mb-2">
              {#each propagationResult.affected_component_ids as componentId}
                {#if componentId !== selectedInitialComponent}
                  <span class="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {scopeComponents.find(c => c.component_id === componentId)?.name || componentId}
                  </span>
                {/if}
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Basic Information Section -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-4">Basic Information</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <!-- Name field -->
        <div class="form-group">
          <label for="name" class="form-label {errors.name ? 'text-red-600' : ''}">
            Name {!viewMode && '*'}
          </label>
          <input 
            type="text" 
            id="name" 
            class="form-input {errors.name ? 'border-red-500' : ''}" 
            bind:value={scenario.name} 
            disabled={viewMode}
            placeholder="E.g., Vehicle Immobilization"
          />
          {#if errors.name}
            <p class="text-red-600 text-sm mt-1">{errors.name}</p>
          {/if}
        </div>
        
        <!-- Category field -->
        <div class="form-group">
          <label for="category" class="form-label {errors.category ? 'text-red-600' : ''}">
            Category {!viewMode && '*'}
          </label>
          <select 
            id="category" 
            class="form-select {errors.category ? 'border-red-500' : ''}" 
            bind:value={scenario.category} 
            disabled={viewMode}
          >
            <option value="" disabled selected>Select a category</option>
            {#each Object.entries(DamageCategory) as [key, value]}
              <option value={value}>{value}</option>
            {/each}
          </select>
          {#if errors.category}
            <p class="text-red-600 text-sm mt-1">{errors.category}</p>
          {/if}
        </div>
      </div>
      
      <!-- Description field -->
      <div class="form-group mb-4">
        <label for="description" class="form-label {errors.description ? 'text-red-600' : ''}">
          Description {!viewMode && '*'}
        </label>
        <textarea 
          id="description" 
          class="form-textarea {errors.description ? 'border-red-500' : ''}" 
          bind:value={scenario.description} 
          disabled={viewMode}
          rows="4"
          placeholder="Detailed description of what could happen if security properties are violated"
        ></textarea>
        {#if errors.description}
          <p class="text-red-600 text-sm mt-1">{errors.description}</p>
        {:else if !viewMode}
          <p class="text-gray-500 text-sm mt-1">Minimum 10 characters</p>
        {/if}
      </div>
      
      <!-- Scope field -->
      <div class="form-group">
        <label for="scope_id" class="form-label {errors.scope_id ? 'text-red-600' : ''}">
          System Scope {!viewMode && '*'}
        </label>
        <select 
          id="scope_id" 
          class="form-select {errors.scope_id ? 'border-red-500' : ''}" 
          bind:value={scenario.scope_id} 
          disabled={viewMode}
        >
          <option value="" disabled selected>Select a system scope</option>
          {#each availableScopes as scope}
            <option value={scope.scope_id}>{scope.name}</option>
          {/each}
        </select>
        {#if errors.scope_id}
          <p class="text-red-600 text-sm mt-1">{errors.scope_id}</p>
        {/if}
      </div>
    </div>
    
    <!-- Additional sections for affected assets, violated properties, and impact types -->
    <!-- Form buttons for submit/cancel -->
    
    {#if editMode}
      <!-- Revision notes field -->
      <div class="form-group mt-6 pt-4 border-t border-gray-200">
        <label for="revision_notes" class="form-label {errors.revision_notes ? 'text-red-600' : ''}">
          Revision Notes {!viewMode && '*'}
        </label>
        <textarea 
          id="revision_notes" 
          class="form-textarea {errors.revision_notes ? 'border-red-500' : ''}" 
          bind:value={scenario.revision_notes} 
          disabled={viewMode}
          rows="2"
          placeholder="Describe what changed in this revision"
        ></textarea>
        {#if errors.revision_notes}
          <p class="text-red-600 text-sm mt-1">{errors.revision_notes}</p>
        {/if}
      </div>
    {/if}
    
    <!-- Form buttons -->
    <div class="mt-6 pt-4 border-t border-gray-200 flex justify-end gap-3">
      <button 
        type="button" 
        class="btn btn-secondary" 
        on:click={handleCancel}
      >
        {viewMode ? 'Close' : 'Cancel'}
      </button>
      
      {#if !viewMode}
        <button 
          type="submit" 
          class="btn btn-primary" 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : editMode ? 'Update Scenario' : 'Create Scenario'}
        </button>
      {/if}
    </div>
  </form>
</div>
```

#### DamageScenarioCard.svelte

Card component to display a damage scenario summary:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Eye, Edit, Trash2 } from '@lucide/svelte';
  import type { DamageScenario } from '../types';
  
  export let scenario: DamageScenario;
  
  const dispatch = createEventDispatcher();
  
  // Helper function to get impact types as a string
  function getImpactTypes(): string {
    const impacts = [];
    if (scenario.safety_impact) impacts.push('Safety');
    if (scenario.financial_impact) impacts.push('Financial');
    if (scenario.operational_impact) impacts.push('Operational');
    if (scenario.privacy_impact) impacts.push('Privacy');
    return impacts.join(', ');
  }
</script>

<div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
  <div class="p-4">
    <h3 class="text-lg font-semibold mb-2">{scenario.name}</h3>
    <p class="text-sm text-gray-600 mb-3 line-clamp-2">{scenario.description}</p>
    
    <div class="flex flex-wrap gap-1 mb-2">
      <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
        {scenario.category}
      </span>
      <span class="px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded-full">
        {getImpactTypes()}
      </span>
    </div>
    
    <div class="text-xs text-gray-500 mb-2">
      <span>Affected Assets: {scenario.affected_assets.length}</span>
    </div>
  </div>
  
  <div class="border-t border-gray-200 bg-gray-50 px-4 py-2 flex justify-end space-x-2">
    <button 
      class="p-1 text-gray-500 hover:text-blue-600 transition-colors"
      on:click={() => dispatch('view')}
    >
      <Eye size={18} />
    </button>
    <button 
      class="p-1 text-gray-500 hover:text-amber-600 transition-colors"
      on:click={() => dispatch('edit')}
    >
      <Edit size={18} />
    </button>
    <button 
      class="p-1 text-gray-500 hover:text-red-600 transition-colors"
      on:click={() => dispatch('delete')}
    >
      <Trash2 size={18} />
    </button>
  </div>
</div>
```

### API Service Implementation

```typescript
// api.ts

export const damageScenarioApi = {
  getAll: async (): Promise<DamageScenario[]> => {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios`);
    if (!response.ok) {
      throw new Error('Failed to fetch damage scenarios');
    }
    return response.json();
  },
  
  getById: async (id: string): Promise<DamageScenario> => {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch damage scenario with ID: ${id}`);
    }
    return response.json();
  },
  
  create: async (scenario: Omit<DamageScenario, 'scenario_id'>): Promise<DamageScenario> => {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario),
    });
    if (!response.ok) {
      throw new Error('Failed to create damage scenario');
    }
    return response.json();
  },
  
  update: async (id: string, scenario: Partial<DamageScenario>): Promise<DamageScenario> => {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario),
    });
    if (!response.ok) {
      throw new Error(`Failed to update damage scenario with ID: ${id}`);
    }
    return response.json();
  },
  
  delete: async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete damage scenario with ID: ${id}`);
    }
  },
  
  getByScope: async (scopeId: string): Promise<DamageScenario[]> => {
    const response = await fetch(`${API_BASE_URL}/scopes/${scopeId}/damage-scenarios`);
    if (!response.ok) {
      throw new Error(`Failed to fetch damage scenarios for scope: ${scopeId}`);
    }
    return response.json();
  },
  
  getByComponent: async (componentId: string): Promise<DamageScenario[]> => {
    const response = await fetch(`${API_BASE_URL}/components/${componentId}/damage-scenarios`);
    if (!response.ok) {
      throw new Error(`Failed to fetch damage scenarios for component: ${componentId}`);
    }
    return response.json();
  }
};
```

## Impact Propagation Engine

A key feature of the Damage Scenarios implementation will be the Impact Propagation Engine, which leverages existing asset information to semi-automate the creation of damage scenarios.

### Concept Overview

The Impact Propagation Engine analyzes the following existing data:

1. **Component CIA Properties**: Security properties already defined for each component
2. **Component Connectivity**: Relationships between components established during asset identification
3. **Trust Boundaries**: Components within the same or different trust zones
4. **Scope Definition**: The system boundary and context

When a user initiates a damage scenario, the engine will:

1. Start with an initial component or impact type
2. Trace the connectivity graph to identify affected components
3. Apply CIA impact propagation rules to determine security property violations
4. Suggest appropriate impact categories based on the affected components

### Propagation Rules

```python
def propagate_impact(initial_component, impact_type):
    """Propagate impact from initial component to connected components"""
    affected_components = [initial_component]
    visited = set([initial_component.component_id])
    queue = [initial_component]
    
    while queue:
        component = queue.pop(0)
        
        # Get directly connected components
        connected_components = get_connected_components(component)
        
        for connected in connected_components:
            if connected.component_id in visited:
                continue
                
            # Apply propagation rules based on impact type and connection type
            if should_propagate(component, connected, impact_type):
                affected_components.append(connected)
                visited.add(connected.component_id)
                queue.append(connected)
    
    return affected_components

def should_propagate(source, target, impact_type):
    """Determine if impact should propagate from source to target"""
    # Rule 1: High integrity components propagate integrity impacts
    if (impact_type == 'integrity' and 
        source.integrity == 'High' and 
        source.trust_zone.value >= target.trust_zone.value):
        return True
        
    # Rule 2: High availability components propagate availability impacts
    if (impact_type == 'availability' and 
        source.availability == 'High'):
        return True
        
    # Rule 3: Confidentiality propagates within the same trust zone
    if (impact_type == 'confidentiality' and 
        source.trust_zone == target.trust_zone and
        source.confidentiality == 'High'):
        return True
        
    # Additional rules based on component types and relationships
    # ...
    
    return False
```

### Damage Category Suggestion

The engine will suggest appropriate damage categories based on the affected components and their properties:

```python
def suggest_damage_category(affected_components, violated_properties):
    """Suggest damage category based on affected components and violated properties"""
    # Check for safety-critical components
    has_safety_critical = any(c.safety_level in ['ASIL C', 'ASIL D'] for c in affected_components)
    
    # Check for external-facing components
    has_external_facing = any(c.location == 'External' for c in affected_components)
    
    # Check for data-handling components
    has_data_handling = any('Personal' in c.data_types for c in affected_components)
    
    # Determine primary violated property
    primary_violation = most_common(violated_properties)
    
    if has_safety_critical and 'availability' in violated_properties:
        return DamageCategory.SAFETY_HAZARD
        
    if has_external_facing and 'integrity' in violated_properties:
        return DamageCategory.VEHICLE_CONTROL
        
    if has_data_handling and 'confidentiality' in violated_properties:
        return DamageCategory.PRIVACY_VIOLATION
        
    if 'availability' in violated_properties:
        return DamageCategory.SERVICE_DISRUPTION
        
    if 'confidentiality' in violated_properties:
        return DamageCategory.DATA_BREACH
        
    # Default
    return DamageCategory.OPERATIONAL_IMPACT
```

## Implementation Strategy

The implementation of the Damage Scenarios module with the Impact Propagation Engine will follow a phased approach to ensure each component is properly developed, tested, and integrated.

### Phase 1: Database Schema and Core Models (Week 1)

1. **Database Schema Setup**
   - Create the `damage_scenarios` table with all required fields
   - Create the `component_damage_scenario` association table for many-to-many relationships
   - Add versioning and soft delete capabilities for audit trails
   - Update existing tables with necessary relationships

2. **Pydantic Models Implementation**
   - Implement DamageScenarioBase, DamageScenarioCreate, and DamageScenarioUpdate models
   - Add comprehensive validation rules for all fields
   - Create enums for damage categories and security properties
   - Implement validation for impact types and affected components

3. **Database Migration Scripts**
   - Create Alembic migration scripts for the new tables
   - Test migrations in development environment
   - Prepare rollback procedures

### Phase 2: Impact Propagation Engine (Week 2)

1. **Core Propagation Algorithm**
   - Implement the graph traversal algorithm for impact propagation
   - Create propagation rules based on CIA properties and component types
   - Develop the damage category suggestion logic
   - Build impact type inference based on component characteristics

2. **Engine Service Layer**
   - Create a dedicated service for the Impact Propagation Engine
   - Implement caching for performance optimization
   - Add logging for debugging and performance monitoring
   - Create unit tests for all propagation rules

3. **Visualization Data Preparation**
   - Prepare data structures for visualizing propagation paths
   - Implement component connectivity graph generation
   - Create helper functions for frontend visualization

### Phase 3: API Endpoints (Week 2-3)

1. **CRUD API Implementation**
   - Implement standard CRUD operations for damage scenarios
   - Add filtering capabilities for all endpoints
   - Implement pagination for list endpoints
   - Create comprehensive error handling

2. **Propagation Engine API**
   - Implement the propagation suggestion endpoint
   - Create endpoints for retrieving propagation rules
   - Add endpoints for component connectivity data
   - Implement category suggestion endpoints

3. **API Testing**
   - Create comprehensive test suite for all endpoints
   - Develop curl command examples for documentation
   - Test performance under various load conditions
   - Validate all error cases and edge conditions

### Phase 4: Frontend Core Components (Week 3-4)

1. **TypeScript Interface Development**
   - Create interfaces for all damage scenario models
   - Implement type definitions for propagation engine responses
   - Add validation types for form handling
   - Create utility types for filtering and sorting

2. **API Service Implementation**
   - Implement the damage scenario API service
   - Create the propagation engine API service
   - Add error handling and retry logic
   - Implement response caching where appropriate

3. **Base Components**
   - Develop the DamageScenarioManager container component
   - Implement the DamageScenarioList component
   - Create the DamageScenarioCard component
   - Build the DamageScenarioFilter component

### Phase 5: Smart Form and Visualization (Week 4-5)

1. **Smart Form Implementation**
   - Develop the DamageScenarioForm with propagation integration
   - Implement dynamic component selection based on scope
   - Create the impact type selection interface
   - Build the suggestion application logic

2. **Propagation Visualization**
   - Implement a graph visualization for impact propagation
   - Create interactive component selection
   - Add path highlighting for propagation routes
   - Implement zooming and panning capabilities

3. **User Experience Enhancements**
   - Add toast notifications for user actions
   - Implement loading states and progress indicators
   - Create helpful tooltips and guidance
   - Build keyboard shortcuts for power users

### Phase 6: Integration and Testing (Week 5-6)

1. **Integration with Existing Modules**
   - Connect with the Component Manager
   - Integrate with the Scope Manager
   - Link to future Threat Scenario module
   - Ensure proper navigation between modules

2. **Comprehensive Testing**
   - Conduct end-to-end testing of the entire workflow
   - Perform usability testing with sample users
   - Test edge cases and error scenarios
   - Validate performance under realistic conditions

3. **Documentation and Training**
   - Create detailed API documentation
   - Develop user guides for the Impact Propagation Engine
   - Prepare training materials for end users
   - Document the propagation rules and algorithms

### Phase 7: Refinement and Enhancement (Ongoing)

1. **User Feedback Integration**
   - Collect and analyze user feedback
   - Refine the propagation rules based on real-world usage
   - Enhance suggestion algorithms
   - Improve visualization based on user needs

2. **Performance Optimization**
   - Optimize database queries for large systems
   - Improve propagation algorithm efficiency
   - Enhance frontend rendering performance
   - Implement advanced caching strategies

3. **Advanced Features**
   - Add batch operations for managing multiple scenarios
   - Implement export/import functionality
   - Create advanced filtering and search capabilities
   - Develop reporting and analytics features

## User Experience Considerations

1. **Guided Creation**: Provide templates and examples to help users create meaningful damage scenarios
2. **Component Integration**: Allow users to easily select affected components and see their security properties
3. **Visualization**: Use visual indicators to show the severity and impact of damage scenarios
4. **Filtering and Sorting**: Enable users to quickly find relevant scenarios based on various criteria
5. **Bulk Operations**: Support batch creation and editing for efficiency

## Security Considerations

1. **Access Control**: Ensure proper authorization for creating and modifying damage scenarios
2. **Validation**: Validate all inputs to prevent injection attacks
3. **Audit Trail**: Log all changes to damage scenarios for compliance and security
4. **Data Protection**: Ensure sensitive scenario details are properly protected

## Testing Strategy

1. **Unit Tests**: Test individual components and services
2. **Integration Tests**: Verify proper interaction between components, scopes, and damage scenarios
3. **API Tests**: Validate all API endpoints with various inputs
4. **UI Tests**: Ensure the user interface works correctly in different scenarios
5. **Security Tests**: Verify proper access controls and input validation

## Next Steps After Implementation

After implementing damage scenarios, the next steps in the TARA process will be:

1. **Impact Rating**: Assess the severity of each damage scenario
2. **Threat Scenario Identification**: Identify specific threats that could cause the damage
3. **Attack Path Analysis**: Analyze how attackers could exploit vulnerabilities to realize threats

These subsequent phases will build upon the damage scenarios created in this phase.
