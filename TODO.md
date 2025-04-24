# QuickTARA Web Implementation Plan

This document outlines the plan to convert QuickTARA into a web-based application using Svelte, Vite, and Tailwind CSS while maintaining the existing Python backend logic.

## Overview

- **Frontend**: Svelte + Vite + Tailwind CSS
- **Backend**: Flask/FastAPI exposing existing Python functionality as APIs
- **Database**: Configurable - SQLite by default, with options for PostgreSQL, MySQL
- **Deployment**: Local-first, with configuration options for intranet/cloud deployment

## Project Structure

```
quicktara/
├── api/                      # API layer (Flask/FastAPI)
│   ├── __init__.py
│   ├── routes/               # API routes
│   │   ├── __init__.py
│   │   ├── components.py     # Component management endpoints
│   │   ├── analysis.py       # Analysis endpoints
│   │   ├── reports.py        # Report generation endpoints
│   │   └── review.py         # Risk review endpoints
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── component.py      # Component model
│   │   ├── analysis.py       # Analysis results model
│   │   ├── report.py         # Report model
│   │   └── review.py         # Review decisions model
│   └── services/             # Business logic adapters
│       ├── __init__.py
│       ├── component_service.py
│       ├── analysis_service.py
│       ├── report_service.py
│       └── review_service.py
├── core/                     # Core analysis logic (existing code)
│   ├── __init__.py
│   ├── quicktara.py          # Main analysis module
│   ├── stride_analysis.py    # STRIDE analysis
│   ├── threat_analysis.py    # Threat analysis
│   ├── attacker_feasibility.py
│   ├── risk_acceptance.py
│   ├── compliance_mappings.py
│   ├── cybersecurity_goals.py
│   └── risk_review.py
├── db/                       # Database layer
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy base configuration
│   ├── session.py            # Session management
│   └── migrations/           # Alembic migrations
├── frontend/                 # Svelte + Vite application
│   ├── src/
│   │   ├── components/       # UI components
│   │   │   ├── ComponentTable.svelte
│   │   │   ├── ThreatAnalysisView.svelte
│   │   │   ├── RiskReviewForm.svelte
│   │   │   └── ...
│   │   ├── api/              # API client functions
│   │   │   ├── index.ts      # API client setup
│   │   │   ├── components.ts
│   │   │   ├── analysis.ts
│   │   │   └── ...
│   │   ├── stores/           # Svelte stores
│   │   │   ├── components.js
│   │   │   ├── analysis.js
│   │   │   └── ...
│   │   ├── views/            # Page views
│   │   │   ├── Home.svelte
│   │   │   ├── Components.svelte
│   │   │   ├── Analysis.svelte
│   │   │   ├── Review.svelte
│   │   │   └── Reports.svelte
│   │   ├── App.svelte        # Main application component
│   │   └── main.js           # Application entry point
│   ├── public/               # Static assets
│   ├── index.html            # HTML template
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── config/                   # Configuration
│   ├── __init__.py
│   ├── default.yaml          # Default configuration
│   └── settings.py           # Configuration loader
├── quicktara_web.py          # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Updated documentation
```

## Implementation Steps

### Phase 1: Backend API Development

1. **Set up project structure**
   - [x] Create the folder structure outlined above
   - [x] Move existing Python code to the `core` directory
   - [x] Create placeholder files for API components

2. **Database Configuration**
   - [x] Set up SQLAlchemy with models reflecting the current data structures
   - [x] Create database abstraction to support multiple database backends
   - [x] Implement configuration system for database selection
   - [ ] Set up Alembic for database migrations

3. **REST API Layer**
   - [x] Choose between Flask and FastAPI (recommended: FastAPI for automatic OpenAPI docs)
   - [x] Implement API endpoints for component management
     - GET/POST/PUT/DELETE for components
     - CSV import/export functionality
   - [x] Implement API endpoints for analysis
     - Trigger analysis
     - Get analysis results
     - Get STRIDE analysis
     - Get compliance mappings
   - [ ] Implement API endpoints for report generation
     - Generate reports in different formats
     - Download reports
   - [ ] Implement API endpoints for risk review
     - Get risk decisions
     - Update risk decisions
     - Submit review comments

4. **Service Layer**
   - [x] Create adapter services that connect API endpoints to core functionality for components
   - [x] Create adapter services that connect API endpoints to core functionality for analysis
   - [ ] Create adapter services for report generation
   - [ ] Create adapter services for risk review

5. **Authentication (if needed)**
   - [ ] Implement basic authentication system
   - [ ] Set up user management API endpoints

### Phase 2: Frontend Development

1. **Setup Svelte + Vite + Tailwind**
   - [x] Initialize Vite project with Svelte template in the `frontend` directory
   - [x] Configure Tailwind CSS
   - [x] Set up TypeScript

2. **API Client**
   - [x] Create API client functions for all backend endpoints
   - [x] Set up error handling and loading states

3. **Component Management UI**
   - [ ] Create component table view
   - [ ] Implement component add/edit forms
   - [ ] Create CSV import interface

4. **Analysis UI**
   - [ ] Implement analysis trigger and progress tracking
   - [ ] Create threat table view with sorting/filtering
   - [ ] Implement STRIDE visualization
   - [ ] Create compliance mapping view

5. **Risk Review UI**
   - [ ] Create risk review interface
   - [ ] Implement decision modification forms
   - [ ] Add justification and evidence fields

6. **Report Generation UI**
   - [ ] Create report configuration options
   - [ ] Implement download functionality

7. **Settings UI**
   - [ ] Create database configuration interface
   - [ ] Implement other settings options

### Phase 3: Integration & Deployment

1. **Integrate Frontend and Backend**
   - [ ] Configure backend to serve the built Svelte application
   - [ ] Set up CORS for development environment
   - [ ] Ensure all API interactions work correctly

2. **Configuration System**
   - [ ] Finalize configuration file format
   - [ ] Implement configuration loading in the application
   - [ ] Create sample configurations for different deployment scenarios

3. **Single-Command Startup**
   - [ ] Enhance `quicktara_web.py` to start both the API server and serve the frontend
   - [ ] Implement command-line arguments for customization

4. **Documentation**
   - [ ] Update README with new setup instructions
   - [ ] Create user guide for the web interface
   - [ ] Document configuration options
   - [ ] Create API documentation (or use auto-generated docs from FastAPI)

5. **Testing**
   - [ ] Create test cases for API endpoints
   - [ ] Test with different database configurations
   - [ ] Perform end-to-end testing of full workflows

### Phase 4: Enhancements & Optimization

1. **Performance Optimization**
   - [ ] Optimize large dataset handling
   - [ ] Implement caching where appropriate
   - [ ] Optimize database queries

2. **UI Enhancements**
   - [ ] Add interactive visualizations for attack paths
   - [ ] Implement dashboard with analysis summaries
   - [ ] Add dark mode support

3. **Collaboration Features (optional)**
   - [ ] Implement project/team concepts if using shared database
   - [ ] Add commenting on analysis results
   - [ ] Create activity logs

## Technical Details

### Database Models

1. **Component Model**
   - Maps to current Component class
   - Stores all component attributes (ID, name, type, interfaces, etc.)

2. **Analysis Model**
   - Stores analysis results for components
   - Links to threats, STRIDE analysis, compliance mappings

3. **Report Model**
   - Stores generated reports
   - Includes metadata like generation time, format, parameters

4. **Review Model**
   - Stores risk review decisions
   - Includes justifications, reviewer information, timestamps

### API Endpoints

1. **Component Management**
   - `GET /api/components` - List all components
   - `GET /api/components/{id}` - Get component details
   - `POST /api/components` - Create new component
   - `PUT /api/components/{id}` - Update component
   - `DELETE /api/components/{id}` - Delete component
   - `POST /api/components/import` - Import components from CSV
   - `GET /api/components/export` - Export components to CSV

2. **Analysis**
   - `POST /api/analysis` - Run analysis on components
   - `GET /api/analysis/{id}` - Get analysis results
   - `GET /api/analysis/{id}/stride` - Get STRIDE analysis
   - `GET /api/analysis/{id}/compliance` - Get compliance mappings
   - `GET /api/analysis/{id}/attack-paths` - Get attack path analysis

3. **Reports**
   - `POST /api/reports` - Generate new report
   - `GET /api/reports` - List available reports
   - `GET /api/reports/{id}` - Download report
   - `DELETE /api/reports/{id}` - Delete report

4. **Risk Review**
   - `GET /api/review/{analysis_id}` - Get risk decisions for review
   - `POST /api/review/{analysis_id}` - Submit risk review
   - `GET /api/review/{analysis_id}/status` - Get review status

### Configuration Options

```yaml
# Database configuration
database:
  type: sqlite  # sqlite, postgresql, mysql
  path: ./quicktara.db  # For SQLite
  host: localhost  # For other databases
  port: 5432  # For other databases
  name: quicktara  # For other databases
  user: username  # For other databases
  password: password  # For other databases

# Server configuration
server:
  host: 127.0.0.1
  port: 8080
  debug: false

# File storage configuration
storage:
  uploads_dir: ./uploads
  reports_dir: ./reports

# Logging configuration
logging:
  level: info  # debug, info, warning, error
  file: ./quicktara.log
```

## Development Approach

1. **Iterative Development**
   - Start with a minimal viable product (MVP) that includes:
     - Component management
     - Basic analysis
     - Simple report generation
   - Add more advanced features iteratively

2. **API-First Development**
   - Develop and test the API endpoints before building the frontend
   - Use tools like Postman or Swagger UI to test the API

3. **Modular Architecture**
   - Keep the core analysis logic separate from the API layer
   - Use dependency injection for database and service components
   - Make components easily replaceable

## Testing the API Endpoints Locally

### Setup

1. **Create a virtual environment and install dependencies**:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

2. **Start the web application**:

```bash
# Start in debug mode for better error messages
python quicktara_web.py --debug
```

The server will start at http://127.0.0.1:8080 by default (or the port specified in your configuration).

3. **Access the API documentation**:

FastAPI provides automatic API documentation. When running in debug mode, you can access:
- OpenAPI UI: http://127.0.0.1:8080/docs
- ReDoc UI: http://127.0.0.1:8080/redoc

### Testing Components API

#### List Components
```
GET http://127.0.0.1:8080/api/components
```

#### Create a Component
```
POST http://127.0.0.1:8080/api/components
Content-Type: application/json

{
  "component_id": "ECU001",
  "name": "Engine Control Unit",
  "type": "ECU",
  "safety_level": "ASIL D",
  "interfaces": ["CAN", "FlexRay"],
  "access_points": ["OBD-II", "Debug Port"],
  "data_types": ["Control Commands", "Sensor Data"],
  "location": "Internal",
  "trust_zone": "Critical",
  "connected_to": []
}
```

#### Get a Component
```
GET http://127.0.0.1:8080/api/components/ECU001
```

#### Update a Component
```
PUT http://127.0.0.1:8080/api/components/ECU001
Content-Type: application/json

{
  "name": "Main Engine Control Unit",
  "type": "ECU",
  "safety_level": "ASIL D",
  "interfaces": ["CAN", "FlexRay"],
  "access_points": ["OBD-II", "Debug Port"],
  "data_types": ["Control Commands", "Sensor Data"],
  "location": "Internal",
  "trust_zone": "Critical",
  "connected_to": []
}
```

#### Delete a Component
```
DELETE http://127.0.0.1:8080/api/components/ECU001
```

#### Import Components from CSV
```
POST http://127.0.0.1:8080/api/components/import
Content-Type: multipart/form-data

# Attach a CSV file with the name "file"
```

#### Export Components to CSV
```
GET http://127.0.0.1:8080/api/components/export
```

### Testing Analysis API

#### Create Components for Testing

First, create multiple components for analysis (you can use the POST example above multiple times with different IDs).

#### Run Analysis
```
POST http://127.0.0.1:8080/api/analysis
Content-Type: application/json

{
  "component_ids": ["ECU001", "ECU002"],
  "name": "Engine Systems Analysis",
  "description": "Analysis of engine control components"
}
```

This will return an analysis ID that you'll use in subsequent requests.

#### List Analyses
```
GET http://127.0.0.1:8080/api/analysis
```

#### Get Analysis Results
```
GET http://127.0.0.1:8080/api/analysis/{analysis_id}
```
Replace `{analysis_id}` with the ID returned from the run analysis request.

#### Get STRIDE Analysis
```
GET http://127.0.0.1:8080/api/analysis/{analysis_id}/stride
```

#### Get Attack Paths
```
GET http://127.0.0.1:8080/api/analysis/{analysis_id}/attack-paths
```

### Using API Testing Tools

You can test these endpoints using tools like:

1. **curl** - Command line tool:
   ```bash
   # Example: List components
   curl http://127.0.0.1:8080/api/components
   
   # Example: Create a component
   curl -X POST http://127.0.0.1:8080/api/components \
     -H "Content-Type: application/json" \
     -d '{"component_id":"ECU001","name":"Engine Control Unit","type":"ECU","safety_level":"ASIL D","interfaces":["CAN","FlexRay"],"access_points":["OBD-II","Debug Port"],"data_types":["Control Commands","Sensor Data"],"location":"Internal","trust_zone":"Critical","connected_to":[]}'  
   ```

2. **Postman** - GUI tool for API testing:
   - Download from https://www.postman.com/
   - Create a new collection for QuickTARA
   - Add requests for each endpoint

3. **Python Requests** - For programmatic testing:
   ```python
   import requests
   import json
   
   # Create a component
   response = requests.post(
       "http://127.0.0.1:8080/api/components",
       json={
           "component_id": "ECU001",
           "name": "Engine Control Unit",
           "type": "ECU",
           "safety_level": "ASIL D",
           "interfaces": ["CAN", "FlexRay"],
           "access_points": ["OBD-II", "Debug Port"],
           "data_types": ["Control Commands", "Sensor Data"],
           "location": "Internal",
           "trust_zone": "Critical",
           "connected_to": []
       }
   )
   print(response.status_code)
   print(response.json())
   ```

### Troubleshooting

1. **Database Issues**:
   - By default, SQLite is used and the database file is created in the project directory
   - Check file permissions if you encounter database access errors

2. **Missing Dependencies**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

3. **API Errors**:
   - Check the server logs for detailed error messages
   - In debug mode, the API will return more detailed error responses

4. **Schema Validation Errors**:
   - If you get 422 Validation Error responses, check the error details in the response
   - Make sure the JSON data matches the expected schema (check the /docs page for schemas)

5. **Database Migration**:
   - If you get "no such table" errors, the database schema might need to be created
   - The application should create tables automatically on first run, but you may need to delete the database file and restart if there are schema changes

## Svelte + Vite + Tailwind Setup

```bash
# Create new Vite project with Svelte template
npm create vite@latest frontend -- --template svelte

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Add Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Configure Tailwind (in tailwind.config.js)
module.exports = {
  content: ['./src/**/*.{html,js,svelte}'],
  theme: {
    extend: {},
  },
  plugins: [],
}

# Add Tailwind directives to CSS (create src/app.css)
@tailwind base;
@tailwind components;
@tailwind utilities;

# Import CSS in main.js
import './app.css'
```

This plan provides a comprehensive roadmap for converting QuickTARA into a web-based application while maintaining its core functionality and adding new capabilities.
