<script lang="ts">
  // SecurityPropertiesWizard.svelte
  import { Info } from '@lucide/svelte';
  
  // Define the security properties interface
  export let values = {
    confidentiality: 'MEDIUM',
    integrity: 'MEDIUM',
    availability: 'MEDIUM',
    authenticity_required: false,
    authorization_required: false
  };
  
  export let onChange: (property: string, value: any) => void;
  
  // Security level options
  const securityLevels = [
    { value: 'HIGH', label: 'High' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'LOW', label: 'Low' },
    { value: 'NOT_APPLICABLE', label: 'Not Applicable' }
  ];
  
  // Helper function to get description based on security level
  function getConfidentialityDescription(level: string): string {
    switch(level) {
      case 'HIGH':
        return 'Example: Personal data, key material, authentication data';
      case 'MEDIUM':
        return 'Example: Configuration data, non-personal identifiers';
      case 'LOW':
        return 'Example: Public environmental data, non-sensitive metrics';
      default:
        return '';
    }
  }
  
  function getIntegrityDescription(level: string): string {
    switch(level) {
      case 'HIGH':
        return 'Example: Brake control, steering inputs, safety-critical sensors';
      case 'MEDIUM':
        return 'Example: Navigation data, camera feeds, diagnostic systems';
      case 'LOW':
        return 'Example: Infotainment, comfort features, usage statistics';
      default:
        return '';
    }
  }
  
  function getAvailabilityDescription(level: string): string {
    switch(level) {
      case 'HIGH':
        return 'Example: Emergency systems, fail-safe components, core ECUs';
      case 'MEDIUM':
        return 'Example: Regular vehicle controls, communication links';
      case 'LOW':
        return 'Example: Convenience features, maintenance interfaces';
      default:
        return '';
    }
  }
</script>

<div class="security-wizard bg-white p-5 rounded-lg border border-gray-200 mb-6">
  <h3 class="text-lg font-semibold text-gray-800 mb-4">Security Properties</h3>
  
  <!-- Confidentiality Question -->
  <div class="wizard-question mb-6">
    <div class="flex items-center mb-1">
      <p class="font-medium text-gray-700">
        Could unauthorized access to this component's data cause harm?
      </p>
      <div class="tooltip ml-2" title="This helps determine the confidentiality level">
        <Info size={16} class="text-gray-500" />
      </div>
    </div>
    <select 
      value={values.confidentiality} 
      on:change={(e) => onChange('confidentiality', e.target.value)}
      class="w-full rounded-md mb-2"
    >
      <option value="HIGH">Yes, severe harm (High)</option>
      <option value="MEDIUM">Yes, moderate harm (Medium)</option>
      <option value="LOW">Minimal harm (Low)</option>
      <option value="NOT_APPLICABLE">Not applicable</option>
    </select>
    <p class="helper-text text-xs text-gray-600">
      {getConfidentialityDescription(values.confidentiality)}
    </p>
  </div>

  <!-- Integrity Question -->
  <div class="wizard-question mb-6">
    <div class="flex items-center mb-1">
      <p class="font-medium text-gray-700">
        Would incorrect data from this component impact safety?
      </p>
      <div class="tooltip ml-2" title="This helps determine the integrity level">
        <Info size={16} class="text-gray-500" />
      </div>
    </div>
    <select 
      value={values.integrity} 
      on:change={(e) => onChange('integrity', e.target.value)}
      class="w-full rounded-md mb-2"
    >
      <option value="HIGH">Yes, safety-critical impacts (High)</option>
      <option value="MEDIUM">Yes, operational impacts (Medium)</option>
      <option value="LOW">Minimal impact (Low)</option>
      <option value="NOT_APPLICABLE">Not applicable</option>
    </select>
    <p class="helper-text text-xs text-gray-600">
      {getIntegrityDescription(values.integrity)}
    </p>
  </div>

  <!-- Availability Question -->
  <div class="wizard-question mb-6">
    <div class="flex items-center mb-1">
      <p class="font-medium text-gray-700">
        Is continuous operation of this component critical?
      </p>
      <div class="tooltip ml-2" title="This helps determine the availability level">
        <Info size={16} class="text-gray-500" />
      </div>
    </div>
    <select 
      value={values.availability} 
      on:change={(e) => onChange('availability', e.target.value)}
      class="w-full rounded-md mb-2"
    >
      <option value="HIGH">Yes, must always be available (High)</option>
      <option value="MEDIUM">Yes, limited downtime acceptable (Medium)</option>
      <option value="LOW">Non-critical operation (Low)</option>
      <option value="NOT_APPLICABLE">Not applicable</option>
    </select>
    <p class="helper-text text-xs text-gray-600">
      {getAvailabilityDescription(values.availability)}
    </p>
  </div>

  <!-- Authenticity Question -->
  <div class="wizard-question checkbox-question mb-4">
    <label class="flex items-start">
      <input 
        type="checkbox" 
        checked={values.authenticity_required}
        on:change={(e) => onChange('authenticity_required', e.target.checked)}
        class="mt-1 mr-2"
      />
      <div>
        <p class="font-medium text-gray-700">Does this component need to verify the source of data it receives?</p>
        <p class="helper-text text-xs text-gray-600 mt-1">
          Important for components that need to trust the source of incoming messages
        </p>
      </div>
    </label>
  </div>

  <!-- Authorization Question -->
  <div class="wizard-question checkbox-question">
    <label class="flex items-start">
      <input 
        type="checkbox" 
        checked={values.authorization_required}
        on:change={(e) => onChange('authorization_required', e.target.checked)}
        class="mt-1 mr-2"
      />
      <div>
        <p class="font-medium text-gray-700">Should this component restrict who/what can access it?</p>
        <p class="helper-text text-xs text-gray-600 mt-1">
          Important for components with sensitive controls or data
        </p>
      </div>
    </label>
  </div>
</div>

<style>
  .tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
  }
  
  .tooltip:hover::after {
    content: attr(title);
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 100%;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    white-space: nowrap;
    z-index: 10;
  }
</style>
