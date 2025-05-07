# Debug Scripts

This directory contains scripts used for debugging and troubleshooting the QuickTARA application.

## Available Scripts

### debug_components.py

**Purpose**: Debug component data structures and relationships.

**Usage**:
```bash
python debug_components.py [component_id]
```

**Description**:
This script inspects and displays detailed information about components in the database. It's useful for debugging component relationship issues, trust zone mappings, and connection problems.

### debug_current_state.py

**Purpose**: Analyze the current application state and identify inconsistencies.

**Usage**:
```bash
python debug_current_state.py
```

**Description**:
This script provides a comprehensive overview of the current application state, including active analyses, component counts, and potential inconsistencies between related data structures. It's helpful for diagnosing issues with analysis results or database state.

### debug_db.py

**Purpose**: Database inspection and debugging utilities.

**Usage**:
```bash
python debug_db.py [--table TABLE_NAME] [--count] [--schema]
```

**Description**:
This script offers various database inspection capabilities:
- View table schemas
- Count records in tables
- Export table data
- Check database integrity

It's useful for troubleshooting database-related issues and verifying data consistency.

## Using Debug Scripts

Debug scripts are intended for development and troubleshooting purposes. They may output sensitive information, so use them in appropriate environments.

Most debug scripts require:
1. A properly configured database connection
2. The QuickTARA environment variables or configuration
3. Appropriate permissions to read database content

## Best Practices

1. Always run debug scripts in a development or test environment, not production
2. Use the output to guide your troubleshooting process
3. Check the script source code for additional options not documented here
