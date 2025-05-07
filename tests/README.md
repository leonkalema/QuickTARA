# QuickTARA Testing Documentation

This directory contains all tests for the QuickTARA project, organized by feature area.

## Directory Structure

- `/tests/api`: Tests for general API functionality
- `/tests/vulnerability`: Tests for vulnerability assessment features
- `/tests/attack_path`: Tests for attack path analysis
- `/tests/risk`: Tests for risk framework and assessments
- `/tests/integration`: End-to-end and integration tests

## Running Tests

The project includes a test runner script that can run all tests or specific test categories:

```bash
# Run all tests
./run_tests.sh --all

# Run specific test categories
./run_tests.sh --api --vulnerability

# Show usage information
./run_tests.sh --help
```

## Test File Naming Conventions

Follow these naming conventions for test files:

- All test files should be prefixed with `test_`
- Use descriptive names that indicate what is being tested
- Format: `test_<feature>_<specific_functionality>.<extension>`
- Example: `test_vulnerability_api.sh`, `test_attack_path_analysis.py`

## Testing Guidelines

### 1. Writing New Tests

When adding new functionality, create corresponding tests:

- **Unit Tests**: Test individual functions or classes
- **API Tests**: Verify API endpoints with curl or similar tools
- **Integration Tests**: Test interactions between multiple components

### 2. Test Coverage

Aim for comprehensive test coverage:

- Core functionality should have both unit and integration tests
- API endpoints should have dedicated test scripts
- Edge cases and error conditions should be tested

### 3. Test Independence

Tests should be independent:

- Each test should set up its own test environment
- Tests should clean up after themselves
- No test should depend on the state created by another test

### 4. Test Data

For consistent test results:

- Use fixture data when possible (found in `/tests/fixtures`)
- Avoid dependencies on external services
- Use mocks for external services when necessary

### 5. Continuous Integration

Tests are run automatically on:

- Pull requests
- Commits to main branches
- Release preparation

### 6. Debugging Failed Tests

If tests fail:

1. Check the test output for specific error messages
2. Run individual test files directly for more verbose output
3. Add debugging output to the test as needed
4. Check the QuickTARA log file for backend errors

## Adding New Test Categories

To add a new test category:

1. Create a new subdirectory under `/tests`
2. Update `run_tests.sh` to include the new category
3. Document the new test category in this README

## Best Practices

1. Write tests before or alongside new code (TDD approach)
2. Keep tests simple and focused on one functionality
3. Use descriptive assertions that provide clear failure messages
4. Regularly run the full test suite to catch regressions
