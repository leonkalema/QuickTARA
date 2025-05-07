# Implementing CIA Security Properties for Components

This implementation guide outlines the steps to add Confidentiality, Integrity, and Availability (CIA) properties to the component model in QuickTARA, using a wizard-style approach for engineers who may not be security experts.

## 1. Backend Changes

### 1.1 Update Component Model (`api/models/component.py`) ✅ COMPLETED

1. Added SecurityLevel enum for CIA properties:
```python
class SecurityLevel(str, Enum):
    """Security levels for CIA properties"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NOT_APPLICABLE = "N/A"
```

2. Added CIA properties to `ComponentBase`:
```python
class ComponentBase(BaseModel):
    # Existing properties...
    
    # Security properties (C-I-A)
    confidentiality: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM,
        description="Degree of protection for data from unauthorized access"
    )
    integrity: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM, 
        description="Degree of protection from improper modification"
    )
    availability: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM,
        description="Degree of reliable accessibility when needed"
    )
    authenticity_required: bool = Field(
        default=False,
        description="Whether data origin authentication is required"
    )
    authorization_required: bool = Field(
        default=False,
        description="Whether access controls are required"
    )
```

3. Fixed `ComponentUpdate` class inheritance and added optional CIA fields:
```python
class ComponentUpdate(BaseModel):  # Changed from ComponentBase to BaseModel
    # Existing fields...
    confidentiality: Optional[SecurityLevel] = None
    integrity: Optional[SecurityLevel] = None
    availability: Optional[SecurityLevel] = None
    authenticity_required: Optional[bool] = None
    authorization_required: Optional[bool] = None
```

4. Added smart defaults logic to automatically suggest appropriate security levels based on component type and safety level:
```python
@validator('confidentiality', 'integrity', 'availability', pre=True)
def set_smart_defaults(cls, v, values):
    # If value is already specified, return it
    if v is not None:
        return v
        
    # Default to MEDIUM if we can't calculate
    if 'type' not in values or 'safety_level' not in values or 'trust_zone' not in values:
        return SecurityLevel.MEDIUM
    
    component_type = values['type']
    safety_level = values['safety_level']
    trust_zone = values['trust_zone']
    
    # Logic for selecting appropriate defaults based on component characteristics
    # Example: For ECUs, high integrity is recommended
    # Example: For safety-critical components (ASIL C/D), high integrity and availability
    
    # Return appropriate security level
    # ...
```

### 1.2 Update Database Model (SQLAlchemy) ✅ COMPLETED

Found and updated the Component model in `/Users/leon/Dev/quicktara/db/base.py`:

```python
class Component(Base):
    """SQLAlchemy model for components"""
    __tablename__ = "components"
    
    # Existing columns...
    
    # Security properties (C-I-A)
    confidentiality = Column(String, default="Medium")
    integrity = Column(String, default="Medium")
    availability = Column(String, default="Medium")
    authenticity_required = Column(Boolean, default=False)
    authorization_required = Column(Boolean, default=False)
```

### 1.3 Create Database Migration ✅ COMPLETED

Created a migration script at `/Users/leon/Dev/quicktara/db/migrations/versions/006_add_security_properties_to_components.py`:

```python
"""\nAdd CIA security properties to components table\n"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_attack_path_analyses_table'

def upgrade():
    # Add security properties columns to components table
    op.add_column('components', sa.Column('confidentiality', sa.String(), nullable=True))
    op.add_column('components', sa.Column('integrity', sa.String(), nullable=True))
    op.add_column('components', sa.Column('availability', sa.String(), nullable=True))
    op.add_column('components', sa.Column('authenticity_required', sa.Boolean(), nullable=True))
    op.add_column('components', sa.Column('authorization_required', sa.Boolean(), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE components SET confidentiality = 'Medium', integrity = 'Medium', availability = 'Medium', authenticity_required = false, authorization_required = false")

def downgrade():
    # Drop security properties columns
    op.drop_column('components', 'confidentiality')
    op.drop_column('components', 'integrity')
    op.drop_column('components', 'availability')
    op.drop_column('components', 'authenticity_required')
    op.drop_column('components', 'authorization_required')
```

### 1.4 Update Component Service (`api/services/component_service.py`) ✅ COMPLETED

Updated the service layer to handle the new security properties:

1. Updated `create_component` function to include CIA properties when creating a new component
2. Updated `_db_component_to_schema` function to include CIA properties when converting database models to Pydantic schemas
3. Added fallbacks for older database records that might not have these properties yet

### 1.5 Update CSV Import/Export Functions ✅ COMPLETED

Updated the CSV import/export functions to include the new security properties:

1. Added CIA security properties to the fieldnames list in `export_components_to_csv`
2. Included CIA security properties in the row data when writing CSV files
3. Updated `import_components_from_csv` to parse CIA security properties from CSV files
4. Added proper handling for boolean values (authenticity_required and authorization_required)

## 2. Frontend Changes

### 2.1 Create Security Properties Wizard Component ✅ COMPLETED

Created a new Svelte component for the wizard-style security properties section at `/Users/leon/Dev/quicktara/frontend/src/components/SecurityPropertiesWizard.svelte`:

```jsx
// SecurityPropertiesWizard.jsx
function SecurityPropertiesWizard({ values, onChange }) {
  return (
    <div className="security-wizard">
      <h3>Security Properties</h3>
      
      {/* Confidentiality Question */}
      <div className="wizard-question">
        <p>
          <strong>Could unauthorized access to this component's data cause harm?</strong>
          <span className="tooltip" title="This helps determine the confidentiality level">ℹ️</span>
        </p>
        <select 
          value={values.confidentiality} 
          onChange={(e) => onChange('confidentiality', e.target.value)}
        >
          <option value="HIGH">Yes, severe harm (High)</option>
          <option value="MEDIUM">Yes, moderate harm (Medium)</option>
          <option value="LOW">Minimal harm (Low)</option>
          <option value="NOT_APPLICABLE">Not applicable</option>
        </select>
        <p className="helper-text">
          {values.confidentiality === "HIGH" && "Example: Personal data, key material, authentication data"}
          {values.confidentiality === "MEDIUM" && "Example: Configuration data, non-personal identifiers"}
          {values.confidentiality === "LOW" && "Example: Public environmental data, non-sensitive metrics"}
        </p>
      </div>

      {/* Integrity Question */}
      <div className="wizard-question">
        <p>
          <strong>Would incorrect data from this component impact safety?</strong>
          <span className="tooltip" title="This helps determine the integrity level">ℹ️</span>
        </p>
        <select 
          value={values.integrity} 
          onChange={(e) => onChange('integrity', e.target.value)}
        >
          <option value="HIGH">Yes, safety-critical impacts (High)</option>
          <option value="MEDIUM">Yes, operational impacts (Medium)</option>
          <option value="LOW">Minimal impact (Low)</option>
          <option value="NOT_APPLICABLE">Not applicable</option>
        </select>
        <p className="helper-text">
          {values.integrity === "HIGH" && "Example: Brake control, steering inputs, safety-critical sensors"}
          {values.integrity === "MEDIUM" && "Example: Navigation data, camera feeds, diagnostic systems"}
          {values.integrity === "LOW" && "Example: Infotainment, comfort features, usage statistics"}
        </p>
      </div>

      {/* Availability Question */}
      <div className="wizard-question">
        <p>
          <strong>Is continuous operation of this component critical?</strong>
          <span className="tooltip" title="This helps determine the availability level">ℹ️</span>
        </p>
        <select 
          value={values.availability} 
          onChange={(e) => onChange('availability', e.target.value)}
        >
          <option value="HIGH">Yes, must always be available (High)</option>
          <option value="MEDIUM">Yes, limited downtime acceptable (Medium)</option>
          <option value="LOW">Non-critical operation (Low)</option>
          <option value="NOT_APPLICABLE">Not applicable</option>
        </select>
        <p className="helper-text">
          {values.availability === "HIGH" && "Example: Emergency systems, fail-safe components, core ECUs"}
          {values.availability === "MEDIUM" && "Example: Regular vehicle controls, communication links"}
          {values.availability === "LOW" && "Example: Convenience features, maintenance interfaces"}
        </p>
      </div>

      {/* Authenticity Question */}
      <div className="wizard-question checkbox-question">
        <label>
          <input 
            type="checkbox" 
            checked={values.authenticity_required}
            onChange={(e) => onChange('authenticity_required', e.target.checked)}
          />
          <strong>Does this component need to verify the source of data it receives?</strong>
        </label>
        <p className="helper-text">
          Important for components that need to trust the source of incoming messages
        </p>
      </div>

      {/* Authorization Question */}
      <div className="wizard-question checkbox-question">
        <label>
          <input 
            type="checkbox" 
            checked={values.authorization_required}
            onChange={(e) => onChange('authorization_required', e.target.checked)}
          />
          <strong>Should this component restrict who/what can access it?</strong>
        </label>
        <p className="helper-text">
          Important for components with sensitive controls or data
        </p>
      </div>
    </div>
  );
}
```

### 2.2 Integrate with Component Form ✅ COMPLETED

Updated the main component form (`/Users/leon/Dev/quicktara/frontend/src/components/ComponentForm.svelte`) to include the new security wizard section:

```jsx
// ComponentForm.jsx
import SecurityPropertiesWizard from './SecurityPropertiesWizard';

// In the form component:
const [securityProps, setSecurityProps] = useState({
  confidentiality: 'MEDIUM',
  integrity: 'MEDIUM',
  availability: 'MEDIUM',
  authenticity_required: false,
  authorization_required: false
});

const handleSecurityChange = (property, value) => {
  setSecurityProps({
    ...securityProps,
    [property]: value
  });
};

// In render/return:
<SecurityPropertiesWizard 
  values={securityProps}
  onChange={handleSecurityChange}
/>
```

### 2.3 Update API Calls ✅ COMPLETED

The API calls are already set up to automatically include all properties of the component object when creating/updating components. Since we've added the security properties to the component object model in the ComponentForm.svelte file, they will be automatically included in the API requests.

### 2.4 Add CSS Styling ✅ COMPLETED

Added CSS styling for the wizard interface in the SecurityPropertiesWizard.svelte component to make it user-friendly:

```css
/* SecurityWizard.css */
.security-wizard {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
  background-color: #f9f9f9;
}

.wizard-question {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.wizard-question:last-child {
  border-bottom: none;
}

.wizard-question select {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-top: 8px;
}

.helper-text {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
  margin-top: 5px;
}

.checkbox-question label {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tooltip {
  cursor: help;
  margin-left: 5px;
}
```

## 3. Implementation Steps Sequence

1. Create a feature branch: `git checkout -b feature/cia-properties`
2. Update the backend model in `api/models/component.py`
3. Update the database model and create migration script
4. Run the database migration
5. Update the component service if needed
6. Update CSV import/export functions
7. Create the frontend wizard component
8. Integrate the wizard with the component form
9. Update API call functions
10. Add CSS styling
11. Test the full flow (component creation and update)
12. Make any fixes based on testing
13. Open a pull request for code review

## 4. Testing Plan

1. Create a new component with security properties
2. Verify the properties are saved correctly in the database
3. Update security properties for an existing component
4. Verify CSV import/export works with the new properties
5. Test edge cases (missing values, etc.)
6. Verify the wizard provides appropriate guidance for non-security experts

## 5. Smart Defaults Logic

Consider implementing smart defaults based on component type and safety level:

```javascript
function getSmartDefaults(componentType, safetyLevel) {
  // Default to medium for everything
  const defaults = {
    confidentiality: 'MEDIUM',
    integrity: 'MEDIUM',
    availability: 'MEDIUM',
    authenticity_required: false,
    authorization_required: false
  };
  
  // For safety-critical components
  if (safetyLevel === 'ASIL_D' || safetyLevel === 'ASIL_C') {
    defaults.integrity = 'HIGH';
    defaults.availability = 'HIGH';
    defaults.authenticity_required = true;
  }
  
  // Type-specific defaults
  switch(componentType) {
    case 'ECU':
      defaults.integrity = 'HIGH';
      defaults.authorization_required = true;
      break;
    case 'SENSOR':
      defaults.integrity = 'HIGH';
      break;
    case 'GATEWAY':
      defaults.confidentiality = 'HIGH';
      defaults.integrity = 'HIGH';
      defaults.authenticity_required = true;
      defaults.authorization_required = true;
      break;
    case 'ACTUATOR':
      defaults.integrity = 'HIGH';
      defaults.availability = 'HIGH';
      break;
  }
  
  return defaults;
}
```

Implement this in the frontend to suggest appropriate values when a user selects a component type or safety level.
