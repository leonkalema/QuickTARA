# SFOP Impact Rating Implementation Guide

## Overview
This feature will add detailed impact ratings to damage scenarios using the SFOP framework:
- **Safety**: Risk to human life, injury, etc.
- **Financial**: Cost of damage, recalls, loss of business
- **Operational**: Disruption to service, degraded performance
- **Privacy**: Exposure of personal or sensitive data

## Implementation Approach

We'll use a hybrid approach that combines automation with user control:

1. **Automatic Rating Generation**: When a damage scenario is created or updated, the system automatically calculates and stores initial SFOP ratings based on component properties and scenario details

2. **Dedicated Impact Rating Tab**: A separate tab in the Analysis Manager for viewing and managing impact ratings across all scenarios

3. **User Review & Control**: Users can review the auto-generated ratings and manually adjust them if needed

## Implementation Steps

### 1. Database Changes
- Add SFOP rating fields to the `DamageScenario` table:
  - `safety_impact`: Enum (Low, Medium, High, Critical)
  - `financial_impact`: Enum (Low, Medium, High, Critical)
  - `operational_impact`: Enum (Low, Medium, High, Critical)
  - `privacy_impact`: Enum (Low, Medium, High, Critical)
  - `impact_rating_notes`: Text field for any manual notes about the ratings
  
- Add audit fields for regulatory compliance (UN R155 and ISO 21434):
  - `sfop_rating_auto_generated`: Boolean indicating if ratings were auto-generated
  - `sfop_rating_last_edited_by`: String for username who last modified the ratings
  - `sfop_rating_last_edited_at`: DateTime when ratings were last modified
  - `sfop_rating_override_reason`: Text field explaining why auto-ratings were overridden
  
- Create a database migration script

### 2. Backend Models and API
- Update Pydantic models to include SFOP fields
- Create an auto-rating algorithm that runs when:
  - A new damage scenario is created
  - Key fields of an existing scenario are updated
- Add API endpoints for:
  - Getting current SFOP ratings for a scenario
  - Updating SFOP ratings manually
  - Getting explanations for auto-generated ratings

### 3. Frontend Implementation
- Create a new "Impact Ratings" tab in the Analysis Manager
- Develop an Impact Rating List component showing all scenarios with their ratings
- Build an Impact Rating Detail view for reviewing and editing ratings
- Add visual indicators (color-coded badges) for each rating level
- Include explanations for how auto-ratings were determined

### 4. Integration
- Show SFOP rating summaries in the Damage Scenarios list
- Add SFOP filtering and sorting options
- Include SFOP ratings in reports and exports

## Technical Details

### Database Migration
```python
# In a new migration file
def upgrade():
    # SFOP rating fields
    op.add_column('damage_scenarios', sa.Column('safety_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('financial_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('operational_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('privacy_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('impact_rating_notes', sa.Text(), nullable=True))
    
    # Audit fields for regulatory compliance
    op.add_column('damage_scenarios', sa.Column('sfop_rating_auto_generated', sa.Boolean(), default=True))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_last_edited_by', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_last_edited_at', sa.DateTime(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_override_reason', sa.Text(), nullable=True))
```

### Auto-Rating Algorithm
The algorithm runs automatically when a damage scenario is created or updated, considering:
1. Component type and function
2. Safety classification (ASIL)
3. Selected damage category
4. CIA impact selections

For example:
- ECUs with ASIL D → High/Critical safety impact
- Telematics components → High privacy impact
- Gateway components → High operational impact

### UI Design
#### Impact Ratings Tab
- New tab in the Analysis Manager alongside Damage Scenarios
- List view showing all scenarios with their SFOP ratings
- Detail view for reviewing and editing a scenario's ratings

#### Visual Elements
- Color-coded impact levels:
  - Low: Green
  - Medium: Yellow
  - High: Orange
  - Critical: Red
- Radar chart visualization of SFOP ratings
- Explanation panel showing how ratings were determined
- Edit mode for manual adjustments


## Detailed Implementation

### Database Schema Updates

#### 1. Update the SQLAlchemy model in `db/damage_scenario.py`:

```python
class DamageScenario(Base):
    """SQLAlchemy model for damage scenarios"""
    __tablename__ = "damage_scenarios"
    
    # Existing fields...
    
    # New SFOP impact fields
    safety_impact = Column(String, nullable=True)
    financial_impact = Column(String, nullable=True)
    operational_impact = Column(String, nullable=True)
    privacy_impact = Column(String, nullable=True)
    impact_rating_notes = Column(Text, nullable=True)
    
    # Audit fields for regulatory compliance (UN R155 and ISO 21434)
    sfop_rating_auto_generated = Column(Boolean, default=True)  # Flag to indicate if ratings were auto-generated
    sfop_rating_last_edited_by = Column(String, nullable=True)  # Username who last modified the ratings
    sfop_rating_last_edited_at = Column(DateTime, nullable=True)  # When ratings were last modified
    sfop_rating_override_reason = Column(Text, nullable=True)  # Reason for overriding auto-ratings
```

#### 2. Create a migration script in `db/migrations/versions/`:

```python
"""Add SFOP impact ratings to damage scenarios

Revision ID: 008_add_sfop_ratings
Revises: 007_add_damage_scenario_tables
Create Date: 2025-05-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '008_add_sfop_ratings'
down_revision = '007_add_damage_scenario_tables'

def upgrade():
    op.add_column('damage_scenarios', sa.Column('safety_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('financial_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('operational_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('privacy_impact', sa.String(), nullable=True))

def downgrade():
    op.drop_column('damage_scenarios', 'safety_impact')
    op.drop_column('damage_scenarios', 'financial_impact')
    op.drop_column('damage_scenarios', 'operational_impact')
    op.drop_column('damage_scenarios', 'privacy_impact')
```

### API Models and Endpoints

#### 1. Update Pydantic models in `api/models/damage_scenario.py`:

```python
class DamageScenarioBase(BaseModel):
    """Base Damage Scenario attributes"""
    # Existing fields...
    
    # SFOP impact ratings
    safety_impact: Optional[SeverityLevel] = Field(None, description="Safety impact rating")
    financial_impact: Optional[SeverityLevel] = Field(None, description="Financial impact rating")
    operational_impact: Optional[SeverityLevel] = Field(None, description="Operational impact rating")
    privacy_impact: Optional[SeverityLevel] = Field(None, description="Privacy impact rating")
    impact_rating_notes: Optional[str] = Field(None, description="Notes about impact ratings")
    
    # Audit fields for regulatory compliance
    sfop_rating_auto_generated: bool = Field(default=True, description="Whether ratings were auto-generated")
    sfop_rating_last_edited_by: Optional[str] = Field(None, description="Username who last modified the ratings")
    sfop_rating_last_edited_at: Optional[datetime] = Field(None, description="When ratings were last modified")
    sfop_rating_override_reason: Optional[str] = Field(None, description="Reason for overriding auto-ratings")

# Add a model for impact rating explanations
class ImpactRatingExplanation(BaseModel):
    """Explanations for impact ratings"""
    safety_impact: str
    financial_impact: str
    operational_impact: str
    privacy_impact: str

# Add a model for impact rating updates
class ImpactRatingUpdate(BaseModel):
    """Model for updating impact ratings"""
    safety_impact: Optional[SeverityLevel] = None
    financial_impact: Optional[SeverityLevel] = None
    operational_impact: Optional[SeverityLevel] = None
    privacy_impact: Optional[SeverityLevel] = None
    impact_rating_notes: Optional[str] = None
    sfop_rating_override_reason: Optional[str] = None  # Required when manually overriding auto-ratings
```

#### 2. Add endpoints for managing impact ratings in `api/routes/damage_scenarios.py`:

```python
@router.get("/{scenario_id}/impact-ratings/explanation", response_model=ImpactRatingExplanation)
async def get_impact_rating_explanation(
    scenario_id: str,
    db: Session = Depends(get_db)
):
    """
    Get explanations for how the impact ratings were determined
    """
    # Get the scenario and component details
    scenario = await get_damage_scenario(scenario_id, db)
    if not scenario:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
        
    # Generate explanations based on component and scenario properties
    explanations = service_generate_impact_explanations(db, scenario)
    return explanations

@router.put("/{scenario_id}/impact-ratings", response_model=DamageScenario)
async def update_impact_ratings(
    scenario_id: str,
    ratings: ImpactRatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update impact ratings for a damage scenario
    """
    # Validate that override reason is provided if auto-generated ratings are being changed
    scenario = await get_damage_scenario(scenario_id, db)
    if not scenario:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
        
    if scenario.sfop_rating_auto_generated and not ratings.sfop_rating_override_reason:
        raise HTTPException(
            status_code=400, 
            detail="Override reason is required when changing auto-generated ratings"
        )
    
    # Add audit information
    ratings_with_audit = ratings.dict(exclude_unset=True)
    ratings_with_audit["sfop_rating_auto_generated"] = False  # Mark as manually edited
    ratings_with_audit["sfop_rating_last_edited_by"] = current_user.username
    ratings_with_audit["sfop_rating_last_edited_at"] = datetime.now()
    
    # Update the scenario
    updated = await service_update_impact_ratings(db, scenario_id, ratings_with_audit)
    if not updated:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
    return updated
```

### Frontend Implementation

#### 1. Create a new Impact Ratings tab in the Analysis Manager:

```svelte
<!-- In AnalysisManager.svelte -->
<script>
  // Add import for the new component
  import ImpactRatingManager from './impact-rating/ImpactRatingManager.svelte';
  
  // Update active tab options
  let activeTab = 'damage-scenarios'; // 'damage-scenarios', 'general-analysis', 'threat-analysis', 'vulnerability-analysis', 'impact-ratings'
</script>

<!-- Add new tab button in the tab navigation -->
<button
  class={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === 'impact-ratings' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
  on:click={() => activeTab = 'impact-ratings'}
>
  <BarChart class="h-5 w-5" />
  <span>Impact Ratings</span>
</button>

<!-- Add new tab content -->
{#if activeTab === 'impact-ratings'}
  <ImpactRatingManager />
{/if}
```

#### 2. Create the ImpactRatingManager component:

```svelte
<!-- In impact-rating/ImpactRatingManager.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { damageScenarioApi } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import { RefreshCw, Edit, Info } from '@lucide/svelte';
  import ImpactRatingList from './ImpactRatingList.svelte';
  import ImpactRatingDetail from './ImpactRatingDetail.svelte';
  
  // State
  let scenarios = [];
  let totalScenarios = 0;
  let isLoading = true;
  let error = '';
  let showDetailPanel = false;
  let selectedScenario = null;
  
  // Fetch all damage scenarios with their impact ratings
  async function loadScenarios() {
    isLoading = true;
    error = '';
    
    try {
      const result = await safeApiCall(() => damageScenarioApi.getAll());
      if (result) {
        scenarios = Array.isArray(result.scenarios) ? result.scenarios : [];
        totalScenarios = result.total || 0;
      }
    } catch (err) {
      console.error('Error loading scenarios:', err);
      error = 'Failed to load scenarios. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  // Handle viewing a scenario's impact ratings
  function handleViewRatings(scenario) {
    selectedScenario = scenario;
    showDetailPanel = true;
  }
  
  // Close the detail panel
  function handleCloseDetail() {
    showDetailPanel = false;
    selectedScenario = null;
  }
  
  // Handle updating impact ratings
  async function handleUpdateRatings(event) {
    const { scenarioId, ratings } = event.detail;
    
    try {
      await safeApiCall(() => damageScenarioApi.updateImpactRatings(scenarioId, ratings));
      await loadScenarios();
      // Refresh the selected scenario if it's still open
      if (selectedScenario && selectedScenario.scenario_id === scenarioId) {
        const updatedScenario = scenarios.find(s => s.scenario_id === scenarioId);
        if (updatedScenario) {
          selectedScenario = updatedScenario;
        }
      }
    } catch (err) {
      console.error('Error updating impact ratings:', err);
    }
  }
  
  onMount(loadScenarios);
</script>

<div class="container mx-auto py-6">
  <h1 class="text-2xl font-bold mb-6">Impact Ratings (SFOP)</h1>
  
  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <p class="text-gray-600">Assess the impact of damage scenarios across Safety, Financial, Operational, and Privacy dimensions</p>
    <button 
      on:click={loadScenarios}
      class="btn btn-secondary flex items-center gap-2"
    >
      <RefreshCw size={16} class={isLoading ? 'animate-spin' : ''} />
      Refresh
    </button>
  </div>
  
  <!-- Content area -->
  <ImpactRatingList 
    {scenarios}
    {isLoading}
    {error}
    on:view={e => handleViewRatings(e.detail)}
  />
  
  <!-- Detail panel (slide-in from right) -->
  {#if showDetailPanel && selectedScenario}
    <ImpactRatingDetail
      scenario={selectedScenario}
      on:close={handleCloseDetail}
      on:update={handleUpdateRatings}
    />
  {/if}
</div>
```

#### 3. Create the ImpactRatingList component:

```svelte
<!-- In impact-rating/ImpactRatingList.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Edit, AlertCircle } from '@lucide/svelte';
  
  // Props
  export let scenarios = [];
  export let isLoading = false;
  export let error = '';
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Get color class based on severity
  function getSeverityColorClass(level) {
    switch (level) {
      case 'Critical': return 'bg-red-100 text-red-800';
      case 'High': return 'bg-orange-100 text-orange-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<div class="bg-white rounded-lg shadow overflow-hidden">
  <!-- Table header -->
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scenario</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Safety</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Financial</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Operational</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Privacy</th>
          <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#if isLoading}
          <tr>
            <td colspan="6" class="px-6 py-4 text-center text-gray-500">Loading impact ratings...</td>
          </tr>
        {:else if error}
          <tr>
            <td colspan="6" class="px-6 py-4">
              <div class="flex items-center text-red-600">
                <AlertCircle size={16} class="mr-2" />
                {error}
              </div>
            </td>
          </tr>
        {:else if scenarios.length === 0}
          <tr>
            <td colspan="6" class="px-6 py-4 text-center text-gray-500">No damage scenarios found.</td>
          </tr>
        {:else}
          {#each scenarios as scenario}
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{scenario.name}</div>
                <div class="text-sm text-gray-500">{scenario.primary_component_id}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.safety_impact)}`}>
                  {scenario.safety_impact || 'Not Rated'}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.financial_impact)}`}>
                  {scenario.financial_impact || 'Not Rated'}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.operational_impact)}`}>
                  {scenario.operational_impact || 'Not Rated'}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.privacy_impact)}`}>
                  {scenario.privacy_impact || 'Not Rated'}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  on:click={() => dispatch('view', scenario)}
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  <Edit size={16} />
                </button>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
```
```

#### 4. Create the ImpactRatingDetail component:

```svelte
<!-- In impact-rating/ImpactRatingDetail.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { X, Save, AlertCircle, Clock, User, FileText } from '@lucide/svelte';
  import { SeverityLevel } from '../../api/damage-scenarios';
  import { showSuccess, showError } from '../ToastManager.svelte';
  import { safeApiCall } from '../../utils/error-handler';
  
  // Props
  export let scenario;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Local state
  let isEditing = false;
  let isSaving = false;
  let editForm = {
    safety_impact: scenario.safety_impact,
    financial_impact: scenario.financial_impact,
    operational_impact: scenario.operational_impact,
    privacy_impact: scenario.privacy_impact,
    impact_rating_notes: scenario.impact_rating_notes || '',
    sfop_rating_override_reason: ''
  };
  
  // Get color class based on severity
  function getSeverityColorClass(level) {
    switch (level) {
      case 'Critical': return 'bg-red-100 text-red-800';
      case 'High': return 'bg-orange-100 text-orange-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Toggle edit mode
  function toggleEditMode() {
    if (isEditing) {
      // Cancel editing
      editForm = {
        safety_impact: scenario.safety_impact,
        financial_impact: scenario.financial_impact,
        operational_impact: scenario.operational_impact,
        privacy_impact: scenario.privacy_impact,
        impact_rating_notes: scenario.impact_rating_notes || '',
        sfop_rating_override_reason: ''
      };
    }
    isEditing = !isEditing;
  }
  
  // Save changes
  async function saveChanges() {
    // Validate that override reason is provided if this is changing auto-generated ratings
    if (scenario.sfop_rating_auto_generated && !editForm.sfop_rating_override_reason) {
      showError('Please provide a reason for overriding the auto-generated ratings');
      return;
    }
    
    isSaving = true;
    
    try {
      dispatch('update', {
        scenarioId: scenario.scenario_id,
        ratings: editForm
      });
      
      isEditing = false;
      showSuccess('Impact ratings updated successfully');
    } catch (err) {
      console.error('Error updating impact ratings:', err);
      showError('Failed to update impact ratings');
    } finally {
      isSaving = false;
    }
  }
  
  // Format date for display
  function formatDate(dateString) {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  }
</script>

<!-- Semi-transparent backdrop -->
<div 
  class="fixed inset-0 bg-neutral-900/40 z-40 transition-opacity duration-200" 
  on:click={() => dispatch('close')}
  on:keydown={(e) => e.key === 'Escape' && dispatch('close')}
  role="button"
  tabindex="0"
  aria-label="Close panel"
></div>

<!-- Slide-in panel from the right -->
<div class="fixed inset-y-0 right-0 w-full md:w-2/3 lg:w-1/2 xl:w-2/5 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out overflow-auto" 
     style="border-left: 1px solid var(--color-border);">
  <div class="h-full overflow-y-auto">
    <div class="p-6 h-full flex flex-col">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6 border-b pb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Impact Rating Details</h2>
          <p class="text-sm text-gray-500 mt-1">{scenario.name}</p>
        </div>
        <button 
          on:click={() => dispatch('close')}
          class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X size={20} />
        </button>
      </div>
      
      <!-- Content -->
      <div class="overflow-y-auto flex-grow">
        {#if isEditing}
          <!-- Edit Form -->
          <div class="space-y-6">
            <!-- Rating Fields -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Safety Impact -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Safety Impact
                </label>
                <select
                  bind:value={editForm.safety_impact}
                  class="form-select w-full rounded-md border-gray-300"
                >
                  <option value={null}>Select Impact Level</option>
                  {#each Object.values(SeverityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
              
              <!-- Financial Impact -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Financial Impact
                </label>
                <select
                  bind:value={editForm.financial_impact}
                  class="form-select w-full rounded-md border-gray-300"
                >
                  <option value={null}>Select Impact Level</option>
                  {#each Object.values(SeverityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
              
              <!-- Operational Impact -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Operational Impact
                </label>
                <select
                  bind:value={editForm.operational_impact}
                  class="form-select w-full rounded-md border-gray-300"
                >
                  <option value={null}>Select Impact Level</option>
                  {#each Object.values(SeverityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
              
              <!-- Privacy Impact -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Privacy Impact
                </label>
                <select
                  bind:value={editForm.privacy_impact}
                  class="form-select w-full rounded-md border-gray-300"
                >
                  <option value={null}>Select Impact Level</option>
                  {#each Object.values(SeverityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
            </div>
            
            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                bind:value={editForm.impact_rating_notes}
                rows="3"
                class="form-textarea w-full rounded-md border-gray-300"
                placeholder="Add any notes about these impact ratings..."
              ></textarea>
            </div>
            
            <!-- Override Reason (only shown for auto-generated ratings) -->
            {#if scenario.sfop_rating_auto_generated}
              <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <AlertCircle size={20} class="text-yellow-600" />
                  </div>
                  <div class="ml-3">
                    <p class="text-sm text-yellow-700">
                      You are overriding auto-generated ratings. Please provide a reason for this change (required for regulatory compliance).
                    </p>
                  </div>
                </div>
                
                <div class="mt-3">
                  <label class="block text-sm font-medium text-yellow-700 mb-1">
                    Override Reason
                  </label>
                  <textarea
                    bind:value={editForm.sfop_rating_override_reason}
                    rows="3"
                    class="form-textarea w-full rounded-md border-yellow-300 bg-yellow-50"
                    placeholder="Explain why you're changing the auto-generated ratings..."
                  ></textarea>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <!-- View Mode -->
          <div class="space-y-6">
            <!-- Impact Ratings Card -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Impact Ratings</h3>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm font-medium text-gray-500">Safety Impact</p>
                  <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.safety_impact)}`}>
                    {scenario.safety_impact || 'Not Rated'}
                  </span>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Financial Impact</p>
                  <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.financial_impact)}`}>
                    {scenario.financial_impact || 'Not Rated'}
                  </span>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Operational Impact</p>
                  <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.operational_impact)}`}>
                    {scenario.operational_impact || 'Not Rated'}
                  </span>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Privacy Impact</p>
                  <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.privacy_impact)}`}>
                    {scenario.privacy_impact || 'Not Rated'}
                  </span>
                </div>
              </div>
              
              {#if scenario.impact_rating_notes}
                <div class="mt-4">
                  <p class="text-sm font-medium text-gray-500">Notes</p>
                  <p class="text-sm mt-1">{scenario.impact_rating_notes}</p>
                </div>
              {/if}
            </div>
            
            <!-- Audit Information Card -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Audit Information</h3>
              
              <div class="space-y-3">
                <div class="flex items-start">
                  <div class="flex-shrink-0 mt-0.5">
                    {#if scenario.sfop_rating_auto_generated}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Auto-Generated
                      </span>
                    {:else}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        Manually Edited
                      </span>
                    {/if}
                  </div>
                </div>
                
                {#if !scenario.sfop_rating_auto_generated}
                  <div class="flex items-start">
                    <User size={16} class="text-gray-400 mr-2 mt-0.5" />
                    <div>
                      <p class="text-sm font-medium text-gray-500">Last Edited By</p>
                      <p class="text-sm">{scenario.sfop_rating_last_edited_by || 'Unknown'}</p>
                    </div>
                  </div>
                  
                  <div class="flex items-start">
                    <Clock size={16} class="text-gray-400 mr-2 mt-0.5" />
                    <div>
                      <p class="text-sm font-medium text-gray-500">Last Edited At</p>
                      <p class="text-sm">{formatDate(scenario.sfop_rating_last_edited_at)}</p>
                    </div>
                  </div>
                  
                  {#if scenario.sfop_rating_override_reason}
                    <div class="flex items-start">
                      <FileText size={16} class="text-gray-400 mr-2 mt-0.5" />
                      <div>
                        <p class="text-sm font-medium text-gray-500">Override Reason</p>
                        <p class="text-sm">{scenario.sfop_rating_override_reason}</p>
                      </div>
                    </div>
                  {/if}
                {/if}
              </div>
            </div>
            
            <!-- Scenario Information -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="font-medium text-gray-900 mb-3">Scenario Information</h3>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm font-medium text-gray-500">Name</p>
                  <p class="text-sm">{scenario.name}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Severity</p>
                  <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColorClass(scenario.severity)}`}>
                    {scenario.severity}
                  </span>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Damage Category</p>
                  <p class="text-sm">{scenario.damage_category}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-500">Impact Type</p>
                  <p class="text-sm">{scenario.impact_type}</p>
                </div>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Footer -->
      <div class="mt-4 pt-4 border-t flex justify-end space-x-3">
        {#if isEditing}
          <button 
            type="button"
            on:click={toggleEditMode}
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            disabled={isSaving}
          >
            Cancel
          </button>
          <button 
            type="button"
            on:click={saveChanges}
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
            disabled={isSaving}
          >
            {#if isSaving}
              <span class="animate-spin">⌛</span>
            {:else}
              <Save size={16} />
            {/if}
            Save Changes
          </button>
        {:else}
          <button 
            type="button"
            on:click={toggleEditMode}
            class="btn btn-primary flex items-center gap-2"
          >
            Edit Ratings
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>
```

#### 5. Update the DamageScenarioView component to display SFOP ratings:

```svelte
<!-- In the view panel of DamageScenarioManager.svelte -->
<!-- SFOP Impact Ratings -->
<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
  <h3 class="font-medium text-gray-900 mb-3">Impact Ratings (SFOP)</h3>
  
  <div class="grid grid-cols-2 gap-4">
    <div>
      <p class="text-sm font-medium text-gray-500">Safety Impact</p>
      <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        {viewingScenario.safety_impact === 'Critical' ? 'bg-red-100 text-red-800' : 
         viewingScenario.safety_impact === 'High' ? 'bg-orange-100 text-orange-800' : 
         viewingScenario.safety_impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
         'bg-green-100 text-green-800'}"
      >
        {viewingScenario.safety_impact || 'Not Rated'}
      </p>
    </div>
    
    <div>
      <p class="text-sm font-medium text-gray-500">Financial Impact</p>
      <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        {viewingScenario.financial_impact === 'Critical' ? 'bg-red-100 text-red-800' : 
         viewingScenario.financial_impact === 'High' ? 'bg-orange-100 text-orange-800' : 
         viewingScenario.financial_impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
         'bg-green-100 text-green-800'}"
      >
        {viewingScenario.financial_impact || 'Not Rated'}
      </p>
    </div>
    
    <div>
      <p class="text-sm font-medium text-gray-500">Operational Impact</p>
      <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        {viewingScenario.operational_impact === 'Critical' ? 'bg-red-100 text-red-800' : 
         viewingScenario.operational_impact === 'High' ? 'bg-orange-100 text-orange-800' : 
         viewingScenario.operational_impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
         'bg-green-100 text-green-800'}"
      >
        {viewingScenario.operational_impact || 'Not Rated'}
      </p>
    </div>
    
    <div>
      <p class="text-sm font-medium text-gray-500">Privacy Impact</p>
      <p class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        {viewingScenario.privacy_impact === 'Critical' ? 'bg-red-100 text-red-800' : 
         viewingScenario.privacy_impact === 'High' ? 'bg-orange-100 text-orange-800' : 
         viewingScenario.privacy_impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
         'bg-green-100 text-green-800'}"
      >
        {viewingScenario.privacy_impact || 'Not Rated'}
      </p>
    </div>
  </div>
</div>
```

### Auto-Suggestion Algorithm Implementation

The core of the SFOP rating system is the suggestion algorithm in the backend service:

```python
# In api/services/damage_scenario_service.py

def suggest_sfop_ratings(
    db: Session,
    component_id: str,
    damage_category: str,
    confidentiality_impact: bool = False,
    integrity_impact: bool = False,
    availability_impact: bool = False
) -> Dict:
    """
    Generate suggested SFOP ratings based on component and damage details
    """
    # Get component details
    component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
    if not component:
        raise ValueError(f"Component with ID {component_id} not found")
    
    # Default ratings
    safety_impact = "Low"
    financial_impact = "Low"
    operational_impact = "Low"
    privacy_impact = "Low"
    
    # Explanations for suggestions
    explanations = {
        "safety_impact": "Default rating based on general component profile.",
        "financial_impact": "Default rating based on general component profile.",
        "operational_impact": "Default rating based on general component profile.",
        "privacy_impact": "Default rating based on general component profile."
    }
    
    # Apply component type rules
    if component.type == "ECU":
        operational_impact = "High"
        explanations["operational_impact"] = "ECUs typically have high operational impact as they control critical vehicle functions."
        
        # Check safety level (ASIL)
        if component.safety_level == "ASIL D":
            safety_impact = "Critical"
            explanations["safety_impact"] = "ASIL D components have critical safety implications."
        elif component.safety_level == "ASIL C":
            safety_impact = "High"
            explanations["safety_impact"] = "ASIL C components have high safety implications."
        elif component.safety_level == "ASIL B":
            safety_impact = "Medium"
            explanations["safety_impact"] = "ASIL B components have medium safety implications."
    
    elif component.type == "Gateway":
        operational_impact = "High"
        explanations["operational_impact"] = "Gateway components are critical for vehicle network communications."
        
        if integrity_impact or availability_impact:
            financial_impact = "Medium"
            explanations["financial_impact"] = "Gateway integrity/availability impacts can lead to significant financial consequences."
    
    elif component.type == "Telematics":
        privacy_impact = "High"
        explanations["privacy_impact"] = "Telematics components handle sensitive user data."
        
        if confidentiality_impact:
            privacy_impact = "Critical"
            explanations["privacy_impact"] = "Confidentiality breaches in telematics can expose sensitive personal data."
    
    # Apply damage category rules
    if damage_category == "Safety":
        safety_impact = max_severity(safety_impact, "Medium")
        explanations["safety_impact"] = "Safety-related damage scenarios have at least medium safety impact."
    
    elif damage_category == "Financial":
        financial_impact = max_severity(financial_impact, "Medium")
        explanations["financial_impact"] = "Financial damage scenarios have at least medium financial impact."
    
    elif damage_category == "Operational":
        operational_impact = max_severity(operational_impact, "Medium")
        explanations["operational_impact"] = "Operational damage scenarios have at least medium operational impact."
    
    elif damage_category == "Privacy":
        privacy_impact = max_severity(privacy_impact, "Medium")
        explanations["privacy_impact"] = "Privacy damage scenarios have at least medium privacy impact."
    
    # Apply CIA impact rules
    if confidentiality_impact and component.confidentiality == "High":
        privacy_impact = max_severity(privacy_impact, "High")
        explanations["privacy_impact"] = "High confidentiality components with confidentiality impact have high privacy implications."
    
    if integrity_impact and component.integrity == "High":
        safety_impact = max_severity(safety_impact, "Medium")
        explanations["safety_impact"] = "High integrity components with integrity impact have at least medium safety implications."
    
    if availability_impact and component.availability == "High":
        operational_impact = max_severity(operational_impact, "High")
        explanations["operational_impact"] = "High availability components with availability impact have high operational implications."
    
    return {
        "safety_impact": safety_impact,
        "financial_impact": financial_impact,
        "operational_impact": operational_impact,
        "privacy_impact": privacy_impact,
        "explanation": explanations
    }

def max_severity(level1: str, level2: str) -> str:
    """Return the higher severity level between two levels"""
    severity_order = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }
    
    return level1 if severity_order.get(level1, 0) >= severity_order.get(level2, 0) else level2
```

## Testing

### API Testing with curl

```bash
# Test SFOP suggestion endpoint
curl -X POST "http://localhost:8080/api/damage-scenarios/suggest-sfop" \
  -H "Content-Type: application/json" \
  -d '{
    "component_id": "comp_123",
    "damage_category": "Safety",
    "confidentiality_impact": false,
    "integrity_impact": true,
    "availability_impact": false
  }'
```

### Frontend Testing

1. Create a new damage scenario
2. Fill in basic information and select a primary component
3. Click "Get Suggestions" to test the suggestion algorithm
4. Apply suggestions and verify they appear in the form
5. Save the scenario and verify SFOP ratings are displayed correctly in the view

## Next Steps

After implementing the SFOP impact ratings, consider these enhancements:

1. Add a radar chart visualization of the SFOP ratings
2. Create a dashboard view showing SFOP distribution across all scenarios
3. Implement filtering and sorting by SFOP ratings
4. Add SFOP ratings to reports and exports
