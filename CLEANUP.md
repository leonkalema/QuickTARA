# QuickTARA Codebase Cleanup Tasks

This document outlines tasks to improve the organization and maintainability of the QuickTARA codebase. Each task should be completed one by one to ensure a systematic improvement of the repository structure.

## Task 1: Consolidate Migration Scripts

- [x] Create a dedicated `/migrations` directory for all database migration scripts
- [x] Move the following files into the new directory:
  - `add_risk_framework_table.py`
  - `add_scope_id_column.py`
  - `add_vulnerability_data.py`
  - `db_create_vulnerability_tables.py`
  - `db_migrate.py`
  - `attack_path_analyses_table.sql`
- [x] Update any references to these files in the codebase
- [x] Add a README.md in the migrations directory explaining the migration workflow

## Task 2: Streamline Test Organization

- [x] Enhance the existing `/tests` directory with subdirectories by feature:
  - `/tests/api`
  - `/tests/vulnerability`
  - `/tests/attack_path`
  - `/tests/risk`
  - `/tests/integration`
- [x] Move the following test scripts into appropriate subdirectories:
  - `test_vulnerability_api.sh`
  - `test_attack_path_api.sh`
  - `test_enhanced_attack_path_api.sh`
  - `test_risk_framework_api.sh`
  - `test_api_direct.js`
  - `test_vulnerability_fix.py`
  - `verify_vulnerability_setup.py`
  - `vulnerability_api_tests.sh`
- [x] Standardize test naming conventions
- [x] Create a test runner script in the root of `/tests`
- [x] Add a README.md in the tests directory explaining the testing workflow and guidelines

## Task 3: Enhance Documentation Structure

- [x] Create a structured `/docs` directory with subdirectories:
  - `/docs/api`: API documentation
  - `/docs/database`: Schema documentation
  - `/docs/workflows`: Process documentation
  - `/docs/standards`: Standard compliance documentation
  - `/docs/guides`: User and developer guides
- [x] Move appropriate `.md` files into the right subdirectories:
  - `IMPLEMENTATION_NOTES.md`
  - `database_migration_notes.md`
  - `database_settings_ui_implementation.md`
  - `VULNERABILITY_API_FIX_SUMMARY.md`
  - `VULNERABILITY_ENDPOINTS_SUMMARY.md`
  - `VULNERABILITY_SETUP_SUMMARY.md`
  - `comprehensive_vulnerability_fix.md`
  - `setup_vulnerability_instructions.md`
  - `vulnerability_fix_instructions.md`
  - Move `/db/docs/vulnerability_db_schema.md` to `/docs/database/`
- [x] Keep high-level docs (README.md, CLEANUP.md, CHECK.md) in the root directory
- [x] Update links in documentation to reflect new locations

## Task 4: Create Scripts Directory

- [x] Create a `/scripts` directory for utility scripts
- [x] Create subdirectories by function:
  - `/scripts/debug`
  - `/scripts/setup`
  - `/scripts/utils`
- [x] Move debugging and setup scripts:
  - `debug_components.py`
  - `debug_current_state.py`
  - `debug_db.py`
  - `setup_vulnerability.sh`
  - `run_vulnerability_fix.sh`
  - `curl_commands.sh`
- [x] Add documentation for each script describing its purpose and usage

## Task 5: Improve Config Management

- [ ] Expand the `/config` directory with environment-specific configurations
- [ ] Create subdirectories:
  - `/config/environments`
  - `/config/schemas`
  - `/config/templates`
- [ ] Add configuration templates for different environments:
  - `development.yaml.template`
  - `production.yaml.template`
  - `testing.yaml.template`
- [ ] Add detailed configuration documentation
- [ ] Implement a configuration validation script

## Task 6: Consolidate Vulnerability Management

- [ ] Create a dedicated module for vulnerability management in `/core/vulnerability`
- [ ] Move all vulnerability-related implementation files:
  - `fix_vulnerability_complete.py`
  - `quick_fix_vulnerability.py`
- [ ] Refactor scattered vulnerability fix scripts into a unified module
- [ ] Update imports and references throughout the codebase
- [ ] Add unit tests for the consolidated functionality

## Task 7: Restructure Core Module

- [ ] Better structure the `/core` directory by functional areas
- [ ] Create subdirectories for different analysis types:
  - `/core/risk`
  - `/core/threat`
  - `/core/vulnerability`
  - `/core/attack_path`
  - `/core/compliance`
- [ ] Move relevant files into the new subdirectories:
  - `stride_analysis.py` → `/core/threat`
  - `threat_analysis.py` → `/core/threat`
  - `attacker_feasibility.py` → `/core/risk`
  - `risk_acceptance.py` → `/core/risk`
  - `cybersecurity_goals.py` → `/core/compliance`
- [ ] Update imports and references throughout the codebase
- [ ] Add __init__.py files to each subdirectory to maintain imports

## Task 8: Enhance API Documentation

- [ ] Create comprehensive OpenAPI/Swagger documentation for all endpoints
- [ ] Move to a dedicated `/api/docs` directory
- [ ] Generate static API documentation
- [ ] Add example requests and responses for each endpoint
- [ ] Create Postman/Insomnia collection for API testing
- [ ] Document authentication and authorization requirements

## Task 9: Clean Up Frontend Structure

- [ ] Organize frontend components by feature
- [ ] Create feature-based directories within `/frontend/src/components/`
- [ ] Standardize component naming conventions
- [ ] Separate UI components from feature components
- [ ] Improve frontend documentation

## Task 10: Review and Update Dependencies

- [ ] Review and update requirements.txt with version pinning
- [ ] Review and update package.json dependencies
- [ ] Remove unused dependencies
- [ ] Document dependency purpose in comments
- [ ] Create separate requirements files for development, production, and testing

## Task 11: Implement CI/CD Configuration

- [ ] Create `.github` directory for GitHub Actions workflow files
- [ ] Implement workflows for:
  - Continuous Integration (testing)
  - Linting and code quality checks
  - Documentation generation
  - Release management
- [ ] Add required configuration files for CI tools
- [ ] Document CI/CD process

## Task 12: Clean Up Root Directory

- [ ] Move all data files to a `/data` directory
- [ ] Remove temporary or obsolete files
- [ ] Ensure all executable scripts have proper permission settings
- [ ] Create a clean entry point for the application
- [ ] Update documentation to reflect the new structure

## Additional Notes

- Consider creating a development guide explaining the codebase organization
- Document the migration process from the old structure to the new one
- Create a style guide for future development
