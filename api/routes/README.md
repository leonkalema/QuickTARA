# QuickTARA API Routes

This directory contains route definitions for the FastAPI application.

## Route Overview

- `components.py`: Routes for component management
- `analysis.py`: Routes for threat analysis
- `reports.py`: Routes for report generation and management
- `review.py`: Routes for risk review workflow

## Risk Review Routes

The risk review API, defined in `review.py`, provides endpoints for managing the risk review workflow:

### Endpoints

1. **Get Risk Decisions for Review**
   ```
   GET /api/review/{analysis_id}
   ```
   - Returns all risks that require review for an analysis, along with their current review status.
   - Response model: `RisksForReviewResponse`

2. **Submit Review Decision**
   ```
   POST /api/review/{analysis_id}/submit
   ```
   - Submits a review decision for a single risk.
   - Request body: `ReviewSubmission`
   - Returns success status and confirmation message.

3. **Submit Batch Review Decisions**
   ```
   POST /api/review/{analysis_id}/batch
   ```
   - Submits multiple review decisions in a single request.
   - Request body: `BatchReviewSubmission`
   - Returns success count, failed count, and total processed.

4. **Get Review Status**
   ```
   GET /api/review/{analysis_id}/status
   ```
   - Returns the current status of the review process for an analysis.
   - Includes total risks, reviewed risks, and pending risks.
   - Response model: `ReviewStatusResponse`

5. **Apply Review Decisions**
   ```
   POST /api/review/{analysis_id}/apply
   ```
   - Applies all review decisions to the analysis and returns the updated analysis.
   - Returns the analysis with applied review decisions.

## Error Handling

All routes implement consistent error handling:

- `404 Not Found`: When a requested resource doesn't exist
- `400 Bad Request`: When request validation fails
- `500 Internal Server Error`: For unexpected server errors

Detailed error messages are provided to help diagnose issues.

## Authentication and Authorization

Currently, these routes don't implement authentication. If authentication is added in the future, appropriate middleware and dependencies will be used to validate requests.

## Route Design Principles

1. **RESTful Design**:
   - Use appropriate HTTP methods for different operations
   - Routes are resource-focused

2. **Consistent Response Format**:
   - Success responses use consistent structure
   - Error responses include detailed information

3. **Path vs. Query Parameters**:
   - Path parameters for resource identifiers
   - Query parameters for filtering, pagination, etc.
