# QuickTARA Scripts

This directory contains utility scripts for the QuickTARA project, organized by function.

## Directory Structure

- [`debug/`](debug/): Scripts for debugging and troubleshooting
  - `debug_components.py`: Utility for debugging component data structures
  - `debug_current_state.py`: Tool for analyzing the current application state
  - `debug_db.py`: Database inspection and debugging utilities

- [`setup/`](setup/): Scripts for setting up and configuring the system
  - `setup_vulnerability.sh`: Script for configuring vulnerability assessment
  - `run_vulnerability_fix.sh`: Script for applying vulnerability fixes

- [`utils/`](utils/): General utility scripts
  - `curl_commands.sh`: Collection of useful API test commands with curl

## Usage Guidelines

1. **Debug Scripts**
   - Run debug scripts when troubleshooting issues
   - Scripts will output detailed information to the console
   - Some debug scripts may require a running database

2. **Setup Scripts**
   - Run setup scripts during initial configuration or when updating
   - Most setup scripts should be run from the project root directory
   - Check script help output for specific usage instructions

3. **Utility Scripts**
   - Reference utility scripts for common tasks
   - Some utility scripts may need to be modified for your environment

## Adding New Scripts

When adding new scripts:

1. Place the script in the appropriate subdirectory
2. Add documentation within the script explaining its purpose and usage
3. Make shell scripts executable with `chmod +x script.sh`
4. Update the relevant README.md file
