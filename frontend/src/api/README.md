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
