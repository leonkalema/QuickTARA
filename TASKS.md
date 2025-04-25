# QuickTARA Web Implementation Tasks

This document tracks the implementation status of the QuickTARA web version and establishes coding standards for the project.

## Implementation Status

### Backend (Python/FastAPI)

#### ✅ Completed
- [x] Project structure setup
- [x] FastAPI application factory
- [x] Database configuration system
- [x] Component models (Pydantic & SQLAlchemy)
- [x] Database session handling
- [x] Configuration system (YAML + env vars)
- [x] Components API endpoints (CRUD operations)
- [x] Component service layer
- [x] CSV import/export functionality
- [x] Main application entry point
- [x] Command-line arguments handling
- [x] Updated requirements.txt

#### 🔄 In Progress
- [x] Analysis service integration
- [x] Report database models
- [x] Report generation service implementation
  - [x] Create service skeleton
  - [x] Implement database operations
  - [x] Implement actual report generation
  - [x] Implement API routes
- [x] Risk review workflow
- [x] Database migrations with Alembic

#### 📝 Pending
- [ ] User authentication (if needed)
- [x] Analysis results database models
- [x] Report database models
- [x] Review decision database models
- [ ] Unit tests for API endpoints
- [ ] Integration tests for services
- [x] Error handling improvements
- [ ] API documentation customization
- [ ] Performance optimizations
- [x] System scope data model and API endpoints

### Frontend (Svelte/Vite/Tailwind)

#### ✅ Completed
- [x] Project initialization (Vite + Svelte)
- [x] Tailwind CSS setup
- [x] TypeScript configuration
- [x] API client functions

#### ✅ Completed
- [x] Component management UI
  - [x] Component list with filtering
  - [x] Component creation/edit form
  - [x] Form validation and error handling
  - [x] CSV import/export
  - [x] Modal UI improvements
- [x] Settings UI
  - [x] Database configuration
  - [x] Connection testing

#### 🔄 In Progress
- [ ] Analysis UI
  - [ ] Analysis request form
  - [ ] Results dashboard

#### 📝 Pending
- [ ] STRIDE visualization
- [ ] Attack path visualization
- [ ] Risk review interface
- [ ] Report generation UI
- [ ] Responsive design
- [ ] Dark/light theme support
- [x] Error handling and notifications
- [ ] Frontend tests

### Integration & Deployment

#### 📝 Pending
- [ ] Frontend build integration with backend
- [ ] Docker configuration
- [ ] CI/CD setup (optional)
- [ ] Deployment documentation
- [ ] User documentation

## Coding Standards

### General Guidelines

1. **File Length**: Keep all files under 350 lines of code
2. **Modular Design**: Single responsibility principle for all modules
3. **Documentation**: All functions, classes, and modules must have docstrings
4. **Type Annotations**: Use Python type hints consistently
5. **Error Handling**: Proper error handling with descriptive messages

### Python/Backend Standards

1. **Code Formatting**
   - Follow PEP 8 style guide
   - Use 4 spaces for indentation
   - Maximum line length of 100 characters
   - Use consistent naming conventions:
     - `snake_case` for variables and functions
     - `PascalCase` for classes
     - `UPPER_CASE` for constants

2. **Imports**
   - Group imports in the following order:
     1. Standard library imports
     2. Third-party imports
     3. Local application imports
   - Use absolute imports for application modules

3. **FastAPI Practices**
   - Use dependency injection for database and services
   - Define request/response models with Pydantic
   - Use appropriate HTTP status codes
   - Use path parameters for resource identifiers
   - Use query parameters for filtering/pagination

4. **Database Operations**
   - Use SQLAlchemy ORM for database operations
   - Keep database logic in service layer
   - Use transactions appropriately
   - Handle database errors gracefully

5. **Testing**
   - Write unit tests for all API endpoints
   - Write integration tests for services
   - Mock external dependencies in tests

### Frontend Standards

1. **Code Formatting**
   - Use 2 spaces for indentation in frontend files
   - Follow Svelte style guide
   - Use ESLint and Prettier for code formatting

2. **Component Design**
   - Keep components small and focused
   - Use props for component configuration
   - Use Svelte stores for state management
   - Separate UI components from logic

3. **CSS/Tailwind**
   - Use utility-first approach with Tailwind
   - Create custom components for repeated patterns
   - Use consistent spacing and sizing
   - Follow responsive design principles

4. **API Integration**
   - Centralize API calls in dedicated modules
   - Handle loading states and errors consistently
   - Use proper error handling and user feedback

5. **Testing**
   - Write unit tests for complex components
   - Test critical user flows

## Git Workflow

1. **Branches**
   - `main`: Production-ready code
   - `develop`: Integration branch for features
   - Feature branches: `feature/feature-name`
   - Bug fixes: `fix/bug-description`

2. **Commits**
   - Use descriptive commit messages
   - Include ticket/issue reference if applicable
   - Keep commits focused on single changes

3. **Pull Requests**
   - Create PRs for feature branches to merge into develop
   - Include description of changes
   - Ensure tests pass before merging

## Definition of Done

A task is considered done when:

1. Code is written according to the standards
2. All tests pass
3. Documentation is updated
4. Code has been reviewed (if applicable)
5. Feature is working as expected in the application

## Next Steps Priority

1. ~~Implement report generation service~~ ✅ (Completed)
2. ~~Implement risk review workflow~~ ✅ (Completed)
3. ~~Set up database migrations with Alembic~~ ✅ (Completed)
4. ~~Create API client functions in frontend~~ ✅ (Completed)
5. ~~Implement database settings UI in frontend~~ ✅ (Completed)
6. ~~Implement Component Management UI~~ ✅ (Completed)
7. ~~Fix Component CRUD issues~~ ✅ (Completed)
8. Implement Analysis UI
9. Create STRIDE visualization
10. Create attack path visualization
11. Implement "Define Scope" feature
    - ✅ Create SystemScope data model and database schema:
      ```python
      # Database model (SQLAlchemy)
      class SystemScope(Base):
          __tablename__ = "system_scopes"
          
          id = Column(Integer, primary_key=True, index=True)
          scope_id = Column(String, unique=True, index=True)
          name = Column(String, nullable=False)
          system_type = Column(String, nullable=False)  # subsystem, API, backend, etc.
          description = Column(Text, nullable=True)
          boundaries = Column(ARRAY(String), nullable=True)
          objectives = Column(ARRAY(String), nullable=True)
          stakeholders = Column(ARRAY(String), nullable=True)
          created_at = Column(DateTime, default=datetime.utcnow)
          updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
          
          # Relationships
          components = relationship("Component", back_populates="scope")
      
      # Update Component model to link with scope
      class Component(Base):
          # existing fields...
          scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=True)
          scope = relationship("SystemScope", back_populates="components")
      ```
      
      ```python
      # Pydantic model
      class SystemScopeCreate(BaseModel):
          name: str
          system_type: str
          description: Optional[str] = None
          boundaries: Optional[List[str]] = []
          objectives: Optional[List[str]] = []
          stakeholders: Optional[List[str]] = []
          
      class SystemScopeResponse(SystemScopeCreate):
          scope_id: str
          created_at: datetime
          updated_at: datetime
          
          class Config:
              orm_mode = True
      ```
    - ✅ Implement scope management backend API:
      - ✅ POST /api/scope (create new scope)
      - ✅ GET /api/scope/{scope_id} (retrieve scope)
      - ✅ PUT /api/scope/{scope_id} (update scope)
      - ✅ GET /api/scope (list all scopes)
      - Add scope_id parameter to component APIs
      - Include scope information in analysis results
    - Create scope management UI components:
      - Add "Scope" navigation item to Navbar.svelte (first item)
      - Create ScopeManager.svelte (main container)
      - Create ScopeForm.svelte (create/edit form)
      - Create TypeScript interface for scope data
      - Update App.svelte to include the new scope page
      - Create scope API client in /api/scope.ts
    - Integrate scope with analysis workflow:
      - Update component creation to include scope reference
      - Include scope information in reports
      - Add scope filtering to component list
      - Update STRIDE analysis to consider system type

