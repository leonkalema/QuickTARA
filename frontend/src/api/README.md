# QuickTARA API Client

This directory contains the API client functions used to interact with the QuickTARA backend services.

## Structure

- `index.ts` - Base API client with request handling functionality
- `api.ts` - Main export module that combines all API services
- `scope.ts` - API client for system scope definition
- `components.ts` - API client for component management
- `analysis.ts` - API client for threat analysis
- `reports.ts` - API client for report generation and management
- `review.ts` - API client for risk review workflow
- `risk.ts` - API client for risk calculation framework management
- `attackPath.ts` - API client for attack path analysis

## Usage

### Importing API Functions

You can import the entire API or individual modules:

```typescript
// Import all API services
import api from '../api/api';

// Import specific API modules
import { componentApi } from '../api/api';
import analysisApi from '../api/analysis';
```

### Working with System Scope

```typescript
import { scopeApi } from '../api/api';
import { SystemScope } from '../api/scope';
import { handleApiError } from '../utils/error-handler';

// Get all scopes
async function loadScopes() {
  try {
    const response = await scopeApi.getAll();
    console.log('Loaded scopes:', response.scopes);
    return response.scopes;
  } catch (error) {
    handleApiError(error, 'Failed to load scopes');
    return [];
  }
}

// Create a new scope
async function createScope(scopeData) {
  try {
    const newScope = await scopeApi.create({
      name: scopeData.name,
      system_type: scopeData.systemType,
      description: scopeData.description,
      boundaries: scopeData.boundaries,
      objectives: scopeData.objectives,
      stakeholders: scopeData.stakeholders
    });
    return newScope;
  } catch (error) {
    handleApiError(error, 'Failed to create scope');
    return null;
  }
}
```

### Working with Components

```typescript
import { componentApi } from '../api/api';
import { Component } from '../api/components';
import { handleApiError } from '../utils/error-handler';

// Get all components
async function loadComponents() {
  try {
    const components = await componentApi.getAll();
    console.log('Loaded components:', components);
    return components;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Create a new component
async function createComponent(component: Component) {
  try {
    const newComponent = await componentApi.create(component);
    console.log('Created component:', newComponent);
    return newComponent;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Import components from CSV
async function importFromCsv(file: File) {
  try {
    const components = await componentApi.importFromCsv(file);
    console.log('Imported components:', components);
    return components;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}
```

### Working with Analysis

```typescript
import { analysisApi } from '../api/api';
import { AnalysisCreate } from '../api/analysis';
import { handleApiError } from '../utils/error-handler';

// Run analysis on components
async function runAnalysis(analysisData: AnalysisCreate) {
  try {
    const analysis = await analysisApi.runAnalysis(analysisData);
    console.log('Analysis started:', analysis);
    return analysis;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Get analysis results
async function getAnalysisResults(analysisId: string) {
  try {
    const results = await analysisApi.getResults(analysisId);
    console.log('Analysis results:', results);
    return results;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Poll for analysis status
async function pollAnalysisStatus(analysisId: string, callback: (status: string, progress?: number) => void) {
  const checkStatus = async () => {
    try {
      const status = await analysisApi.getStatus(analysisId);
      callback(status.status, status.progress);
      
      if (status.status === 'running') {
        setTimeout(checkStatus, 2000); // Check again in 2 seconds
      }
    } catch (error) {
      handleApiError(error);
    }
  };
  
  checkStatus();
}
```

### Working with Reports

```typescript
import { reportsApi } from '../api/api';
import { ReportRequest, ReportFormat } from '../api/reports';
import { handleApiError } from '../utils/error-handler';

// Generate a report
async function generateReport(analysisId: string, format: ReportFormat) {
  try {
    const reportRequest: ReportRequest = {
      analysis_id: analysisId,
      format,
      include_review_status: true
    };
    
    const report = await reportsApi.generateReport(reportRequest);
    console.log('Generated report:', report);
    return report;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Download a report
function downloadReport(reportId: string) {
  const downloadUrl = reportsApi.getDownloadUrl(reportId);
  window.open(downloadUrl, '_blank');
}

// Generate and immediately download a report
async function generateAndDownloadReport(analysisId: string, format: ReportFormat) {
  try {
    const reportRequest: ReportRequest = {
      analysis_id: analysisId,
      format,
      include_review_status: true
    };
    
    await reportsApi.generateAndDownload(reportRequest);
  } catch (error) {
    handleApiError(error);
  }
}
```

### Working with Risk Reviews

```typescript
import { reviewApi } from '../api/api';
import { RiskReviewDecision } from '../api/review';
import { handleApiError } from '../utils/error-handler';

// Get all risk decisions for an analysis
async function getReviewDecisions(analysisId: string) {
  try {
    const decisions = await reviewApi.getDecisions(analysisId);
    console.log('Review decisions:', decisions);
    return decisions;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Submit a risk decision review
async function submitDecisionReview(decision: RiskReviewDecision) {
  try {
    const updatedDecision = await reviewApi.submitDecision(decision);
    console.log('Submitted decision:', updatedDecision);
    return updatedDecision;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Get review status
async function getReviewProgress(analysisId: string) {
  try {
    const status = await reviewApi.getReviewStatus(analysisId);
    console.log('Review status:', status);
    return status;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}
```

### Error Handling

The API client includes built-in error handling that converts HTTP errors into structured `ApiError` objects. You can use the error handling utilities for consistent error handling:

```typescript
import { safeApiCall } from '../utils/error-handler';

// Using the safe API call wrapper
async function loadComponentsSafely() {
  const components = await safeApiCall(() => componentApi.getAll());
  
  if (components) {
    // Handle success
    console.log('Components loaded:', components);
  }
  // No need for try/catch as errors are handled by safeApiCall
}

// Setting a global error handler
import { setGlobalErrorHandler } from '../utils/error-handler';

// Set up global error handling (typically in your app initialization)
setGlobalErrorHandler((error) => {
  // Show error notification to user
  if (error.status === 401) {
    // Handle authentication error
    console.error('Authentication error');
  } else {
    // Handle other errors
    console.error('API error:', error.message);
  }
});
```

## TypeScript Interfaces

All API functions are fully typed with TypeScript interfaces for request and response data. This provides autocompletion and type checking in your IDE.

## Configuration

The API client uses configuration values from `src/config/index.ts`. You can modify these settings to point to different API environments:

```typescript
// src/config/index.ts
export const apiBaseUrl = 'http://localhost:8080/api'; // Development
// export const apiBaseUrl = '/api'; // Production
```

### Working with Risk Frameworks

```typescript
import { 
  getRiskFrameworks,
  getActiveRiskFramework,
  getRiskFramework,
  createRiskFramework,
  updateRiskFramework,
  setRiskFrameworkActive,
  deleteRiskFramework,
  type RiskFramework,
  type RiskFrameworkCreate,
  type RiskFrameworkUpdate
} from '../api/risk';
import { handleApiError } from '../utils/error-handler';

// Get all risk frameworks
async function loadRiskFrameworks() {
  try {
    const response = await getRiskFrameworks();
    console.log('Risk frameworks:', response.frameworks);
    return response.frameworks;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Get the active risk framework
async function getActive() {
  try {
    const framework = await getActiveRiskFramework();
    console.log('Active framework:', framework);
    return framework;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Create a new risk framework
async function createNewFramework(frameworkData: RiskFrameworkCreate) {
  try {
    const framework = await createRiskFramework(frameworkData);
    console.log('Created framework:', framework);
    return framework;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Update an existing risk framework
async function updateFramework(frameworkId: string, updateData: RiskFrameworkUpdate) {
  try {
    const framework = await updateRiskFramework(frameworkId, updateData);
    console.log('Updated framework:', framework);
    return framework;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Set a framework as active
async function setActive(frameworkId: string) {
  try {
    const framework = await setRiskFrameworkActive(frameworkId);
    console.log('Set active framework:', framework);
    return framework;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Delete a risk framework
async function deleteFramework(frameworkId: string) {
  try {
    await deleteRiskFramework(frameworkId);
    console.log('Deleted framework:', frameworkId);
    return true;
  } catch (error) {
    handleApiError(error);
    return false;
  }
}
```

### STRIDE Threat Catalog and Analysis

The QuickTARA API provides a comprehensive threat catalog and STRIDE-based threat analysis system. This API allows you to manage predefined threats and perform automated threat analysis on your system components.

```typescript
import { 
  getThreatCatalogItems,
  getThreatCatalogItem,
  createThreatCatalogItem,
  updateThreatCatalogItem,
  deleteThreatCatalogItem,
  performThreatAnalysis,
  type ThreatCatalogItem,
  type ThreatCatalogCreate,
  type ThreatCatalogUpdate,
  type ThreatAnalysisRequest,
  type ThreatAnalysisResponse,
  StrideCategory,
  ComponentType,
  TrustZone,
  AttackVector
} from '../api/threat';
import { handleApiError } from '../utils/error-handler';

// Get all threat catalog items
async function loadThreatCatalog() {
  try {
    const response = await getThreatCatalogItems();
    console.log('Threat catalog items:', response.catalog_items);
    return response.catalog_items;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Get threat catalog items by STRIDE category
async function loadThreatsByCategory(category: StrideCategory) {
  try {
    const response = await getThreatCatalogItems(0, 100, category);
    console.log(`${category} threats:`, response.catalog_items);
    return response.catalog_items;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Get a specific threat by ID
async function getThreat(threatId: string) {
  try {
    const threat = await getThreatCatalogItem(threatId);
    console.log('Threat details:', threat);
    return threat;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Create a new threat catalog item
async function createThreat(threatData: ThreatCatalogCreate) {
  try {
    const threat = await createThreatCatalogItem(threatData);
    console.log('Created threat:', threat);
    return threat;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Update an existing threat
async function updateThreat(threatId: string, updateData: ThreatCatalogUpdate) {
  try {
    const threat = await updateThreatCatalogItem(threatId, updateData);
    console.log('Updated threat:', threat);
    return threat;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Delete a threat from the catalog
async function deleteThreat(threatId: string) {
  try {
    await deleteThreatCatalogItem(threatId);
    console.log('Deleted threat:', threatId);
    return true;
  } catch (error) {
    handleApiError(error);
    return false;
  }
}

// Perform STRIDE threat analysis on components
async function analyzeThreatsByStride(componentIds: string[], riskFrameworkId?: string) {
  try {
    // Simplified API call with direct component IDs
    const analysis = await performThreatAnalysis(componentIds, [], riskFrameworkId);
    console.log('Threat analysis results:', analysis);
    return analysis;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}
```

#### Example: Creating a New Threat Catalog Item

```typescript
// Example of creating a new threat for the catalog
const newThreat: ThreatCatalogCreate = {
  title: "Battery Data Tampering",
  description: "An attacker manipulates the battery management data to cause overcharging or deep discharge",
  stride_category: StrideCategory.TAMPERING,
  applicable_component_types: [ComponentType.SENSOR, ComponentType.CONTROLLER],
  applicable_trust_zones: [TrustZone.SECURE, TrustZone.TRUSTED],
  attack_vectors: [AttackVector.PHYSICAL, AttackVector.CAN_BUS],
  prerequisites: ["Physical access to vehicle", "CAN bus access"],
  typical_likelihood: 3,
  typical_severity: 5,
  mitigation_strategies: [{
    title: "Message authentication",
    description: "Implement cryptographic message authentication for all battery management messages",
    effectiveness: 4,
    implementation_complexity: 3,
    references: ["ISO 21434", "SAE J3061"]
  }],
  cwe_ids: ["CWE-345"],
  capec_ids: ["CAPEC-176"],
  examples: ["Compromised BMS firmware", "CAN bus spoofing"]
};

const createdThreat = await createThreat(newThreat);
```

#### Example: Analyzing Components for Threats

```typescript
// Analyze multiple components using STRIDE
const componentIds = ["BMS001", "BMS002", "ECU003"];
const analysisResults = await analyzeThreatsByStride(componentIds);

// Access analysis results
if (analysisResults) {
  console.log(`Total threats found: ${analysisResults.total_threats}`);
  console.log(`High risk threats: ${analysisResults.high_risk_threats}`);
  
  // The API can return results in different formats, which are now normalized by the UI
  
  // If using component_analyses format (newer API version)
  if (analysisResults.component_analyses) {
    analysisResults.component_analyses.forEach(analysis => {
      console.log(`${analysis.component_id}: ${analysis.threats?.length || 0} threats`);
      
      // Process threats for this component
      if (analysis.threats) {
        analysis.threats.forEach(threat => {
          console.log(`- ${threat.title} (Risk: ${threat.risk_level})`);
        });
      }
    });
  }
  
  // If using component_threat_profiles format (older API version)
  if (analysisResults.component_threat_profiles) {
    // Group threats by component
    const threatsByComponent = {};
    analysisResults.component_threat_profiles.forEach(profile => {
      if (!threatsByComponent[profile.component_id]) {
        threatsByComponent[profile.component_id] = [];
      }
      threatsByComponent[profile.component_id].push(profile);
    });
    
    // Display threats by component
    Object.entries(threatsByComponent).forEach(([componentId, profiles]) => {
      console.log(`${componentId}: ${profiles.length} threats`);
      profiles.forEach(profile => {
        console.log(`- ${profile.title} (Risk score: ${profile.risk_score})`);
      });
    });
  }
}
```

## Recent Updates (April 2025)

### Attack Path Endpoints Update

The attack path API endpoints have been standardized and now follow a consistent pattern with other API endpoints:

1. **New Endpoint Structure**:
   - `/api/attack-paths` - List and create attack paths
   - `/api/attack-paths/{path_id}` - Get a specific attack path
   - `/api/attack-paths/chains` - List attack chains
   - `/api/attack-paths/chains/{chain_id}` - Get a specific attack chain

2. **Previous Structure** (no longer in use):
   - `/api/analysis/attack-paths`
   - `/api/analysis/attack-paths/{path_id}`
   - `/api/analysis/attack-chains`
   - `/api/analysis/attack-chains/{chain_id}`

3. **Frontend Integration**: The frontend API client in `attackPath.ts` has been updated to use the new endpoints

### Working with Attack Paths

```typescript
import { 
  generateAttackPaths,
  getAttackPaths,
  getAttackPath,
  getAttackChains,
  getAttackChain,
  type AttackPathRequest,
  type AttackPath,
  type AttackChain,
  type AttackPathList,
  type AttackChainList,
  type AttackPathAnalysisResult
} from '../api/attackPath';
import { handleApiError } from '../utils/error-handler';

// Generate attack paths for a set of components
async function analyzeAttackPaths(componentIds: string[]) {
  try {
    const request: AttackPathRequest = {
      component_ids: componentIds,
      include_chains: true,
      max_depth: 5
    };
    
    const result = await generateAttackPaths(request);
    console.log('Attack path analysis result:', result);
    return result;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Get all attack paths
async function loadAttackPaths(analysisId?: string) {
  try {
    const response = await getAttackPaths(analysisId);
    console.log('Attack paths:', response.paths);
    return response.paths;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Get a specific attack path
async function loadAttackPath(pathId: string) {
  try {
    const path = await getAttackPath(pathId);
    console.log('Attack path details:', path);
    return path;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}

// Get all attack chains
async function loadAttackChains(analysisId?: string) {
  try {
    const response = await getAttackChains(analysisId);
    console.log('Attack chains:', response.chains);
    return response.chains;
  } catch (error) {
    handleApiError(error);
    return [];
  }
}

// Get a specific attack chain
async function loadAttackChain(chainId: string) {
  try {
    const chain = await getAttackChain(chainId);
    console.log('Attack chain details:', chain);
    return chain;
  } catch (error) {
    handleApiError(error);
    return null;
  }
}
```

### Threat Analysis Improvements

The threat analysis functionality has been enhanced with the following features:

1. **Simplified API Calls**: The `performThreatAnalysis` function now accepts component IDs directly and handles request formatting internally

2. **Response Format Normalization**: The UI now normalizes different API response formats (both `component_analyses` and `component_threat_profiles` structures) into a consistent format for display

3. **Comprehensive Documentation**: Added JSDoc comments to all API functions for better developer experience

4. **Robust Error Handling**: Improved error handling for API responses with detailed error messages

5. **Component Selection**: Enhanced component selection functionality for easier threat analysis

## Authentication

If the API requires authentication, the client is set up to include credentials with requests using `credentials: 'include'`. This will send cookies along with the requests, which can be used for session-based authentication.

For token-based authentication, you would typically add an Authorization header to requests. You can modify the API client to include authentication tokens automatically:

```typescript
// Add authentication token to requests
const headers = {
  'Accept': 'application/json',
  'Authorization': `Bearer ${getAuthToken()}`,
  ...options.headers || {}
};
```
