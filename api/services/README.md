# QuickTARA API Services

This directory contains service classes that implement the business logic for the QuickTARA API.

## Service Overview

- `component_service.py`: Services for component management
- `analysis_service.py`: Services for threat analysis
- `report_service.py`: Services for report generation
- `review_service.py`: Services for risk review workflow

## Risk Review Service

The `ReviewService` in `review_service.py` implements the complete risk review workflow:

### Key Functionalities

1. **Loading and Saving Review Decisions**
   - `get_review_file_path`: Gets the path to the review file for an analysis
   - `load_review_decisions`: Loads existing review decisions from file
   - `save_review_decisions`: Saves review decisions to file

2. **Retrieving Risks for Review**
   - `get_risks_for_review`: Gets all risks for an analysis that require review
   - `get_review_status`: Gets the status of the review process for an analysis

3. **Submitting Review Decisions**
   - `submit_review`: Submits a review decision for a risk
   - `submit_batch_review`: Submits multiple review decisions at once

4. **Applying Reviews to Analysis**
   - `apply_reviews_to_analysis`: Applies review decisions to an analysis and returns the updated analysis

### Integration with Core Module

The review service integrates with the core risk review functionality by:

1. Converting API models to core models using the appropriate type conversions
2. Using the `apply_review_decisions` function from the core module to apply reviews
3. Handling file storage for review decisions

### API Endpoints

The review service is exposed through the following API endpoints:

- `GET /api/review/{analysis_id}`: Get risks that require review
- `POST /api/review/{analysis_id}/submit`: Submit a review decision
- `POST /api/review/{analysis_id}/batch`: Submit multiple review decisions
- `GET /api/review/{analysis_id}/status`: Get review status
- `POST /api/review/{analysis_id}/apply`: Apply reviews to analysis

## Service Design Principles

1. **Separation of Concerns**:
   - Each service focuses on a specific domain (components, analysis, reports, reviews)
   - Services handle business logic and data transformation

2. **Stateless Design**:
   - Services use static methods for operations
   - State is stored in the database or filesystem, not in memory

3. **Integration with Core Logic**:
   - Services integrate with the core QuickTARA functionality while providing API-friendly interfaces
   - Type conversion between API models and core models is handled in the services
