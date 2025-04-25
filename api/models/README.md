# QuickTARA API Models

This directory contains Pydantic models for the QuickTARA API.

## Model Overview

- `component.py`: Models for component management
- `analysis.py`: Models for threat analysis
- `report.py`: Models for report generation
- `review.py`: Models for risk review workflow
- `scope.py`: Models for system scope definition

## Risk Review Workflow

The risk review workflow allows:

1. Retrieving risks that require review from an analysis
2. Submitting review decisions for risks
3. Tracking the overall review status
4. Applying review decisions to generate final reports

The workflow integrates with the core risk review functionality to provide a complete implementation of the risk review requirements.

This directory contains Pydantic models for API requests and responses.

## Component Models (`component.py`)

Models for managing automotive system components:

- `AssetType` - Enum for component types (ECU, Sensor, Gateway, etc.)
- `SafetyLevel` - Enum for safety levels (ASIL A-D)
- `TrustZone` - Enum for security trust zones
- `ComponentBase` - Base attributes for components including scope association
- `ComponentCreate` - Model for creating new components
- `ComponentUpdate` - Model for updating existing components
- `Component` - Complete component model
- `ComponentList` - List of components with pagination

Each component can be associated with a system scope through the `scope_id` field, which establishes a relationship between the component and its parent scope.

## Analysis Models (`analysis.py`)

Models for threat analysis and risk assessment:

- `StrideCategory` - Enum for STRIDE attack categories
- `ImpactScore` - Impact scores for different categories (financial, safety, privacy)
- `RiskFactors` - Component risk factors (exposure, complexity, attack surface)
- `Threat` - Threat model for a component
- `StrideRecommendation` - STRIDE analysis recommendation
- `ComplianceRequirement` - Compliance mapping to standards
- `AttackerProfile` - Attacker profile assessment
- `AttackerFeasibility` - Attacker feasibility assessment
- `RiskAcceptanceDecision` - Enum for risk acceptance decisions
- `RiskSeverity` - Enum for risk severity levels
- `RiskAcceptance` - Risk acceptance assessment
- `AttackPath` - Attack path between components
- `ComponentAnalysis` - Analysis results for a single component
- `AnalysisCreate` - Request model for creating a new analysis
- `AnalysisSummary` - Summary of analysis results
- `Analysis` - Complete analysis model
- `AnalysisList` - List of analyses with pagination

## Report Models (`report.py`)

Models for report generation and management:

- `ReportFormat` - Enum for report export formats (TXT, JSON, XLSX, PDF)
- `ReportStatus` - Enum for report generation status (PENDING, GENERATING, COMPLETED, FAILED)
- `ReportType` - Enum for report types (PRELIMINARY, FINAL)
- `ReportConfiguration` - Configuration options for report generation
- `ReportCreate` - Request model for creating a new report
- `Report` - Complete report model
- `ReportSummary` - Summary of a report for listings
- `ReportList` - List of reports with pagination
- `ReportError` - Error information for failed reports

## Review Models (`review.py`)

Models for risk review workflow:

- `ReviewStatus` - Enum for review status (PENDING, IN_PROGRESS, COMPLETED)
- `ReviewDecision` - Records a manual review decision for a risk treatment
- `ComponentReviewDecisions` - Review decisions for a single component
- `ReviewSubmission` - Model for submitting review decisions
- `BatchReviewSubmission` - Model for submitting multiple review decisions at once
- `ReviewStatusResponse` - Response model for review status
- `RiskForReview` - Model for a risk requiring review
- `RisksForReviewResponse` - Response model for risks requiring review

## Scope Models (`scope.py`)

Models for defining system boundaries and assessment scope:

- `SystemScope` - Defines a boundary for security assessment including:
  - `name` - Name of the system or subsystem
  - `system_type` - Type of system (subsystem, embedded, network, etc.)
  - `description` - Detailed description of what's included in the scope
  - `boundaries` - List of defined scope boundaries
  - `objectives` - List of assessment objectives
  - `stakeholders` - List of relevant stakeholders
  - `scope_id` - Unique identifier for the scope

- `ScopeCreate` - Model for creating new system scopes
- `ScopeUpdate` - Model for updating existing scopes
- `ScopeList` - List of scopes with pagination

## Scope-Component Relationship

Components are assigned to scopes through the `scope_id` field in the Component model. This relationship establishes a hierarchy where:

1. A scope defines the system boundaries and objectives for assessment
2. Components are then associated with that scope
3. Analysis is performed on components within a specific scope

This enables segmented analysis and reporting based on different system boundaries.

## Database Models

These Pydantic models are used for API request/response handling and validation. The corresponding SQLAlchemy models for database operations are defined in `/db/base.py`.
