# Setup Scripts

This directory contains scripts for setting up and configuring various aspects of the QuickTARA system.

## Available Scripts

### setup_vulnerability.sh

**Purpose**: Configure the vulnerability assessment module.

**Usage**:
```bash
./setup_vulnerability.sh [--database DB_PATH]
```

**Description**:
This script sets up the vulnerability assessment system by:
- Creating necessary database tables
- Loading initial CVE/CWE data
- Configuring vulnerability scanning settings
- Setting up the mapping between vulnerabilities and components

It's essential to run this script before using the vulnerability assessment features.

### run_vulnerability_fix.sh

**Purpose**: Apply fixes to the vulnerability assessment system.

**Usage**:
```bash
./run_vulnerability_fix.sh
```

**Description**:
This script applies fixes to the vulnerability assessment system, including:
- Schema updates
- Data corrections
- API endpoint fixes
- Connection fixes between vulnerability databases and component models

Run this script if you encounter issues with the vulnerability assessment features.

## Common Setup Workflow

1. Initial setup:
   ```bash
   # From project root directory
   ./scripts/setup/setup_vulnerability.sh
   ```

2. If issues are encountered:
   ```bash
   # From project root directory
   ./scripts/setup/run_vulnerability_fix.sh
   ```

3. Verify setup:
   ```bash
   # Using curl to test endpoints
   curl http://localhost:8080/api/vulnerabilities
   ```

## Notes

- These setup scripts should be run from the project root directory
- Some scripts may require sudo privileges depending on your environment
- Always backup your database before running setup scripts that modify schema
- Check the console output for any errors during setup
