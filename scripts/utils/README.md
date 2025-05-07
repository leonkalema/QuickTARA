# Utility Scripts

This directory contains general utility scripts for working with the QuickTARA application.

## Available Scripts

### curl_commands.sh

**Purpose**: Provides examples of API interactions using curl.

**Usage**:
```bash
# View the script to see available commands
cat curl_commands.sh

# Run a specific command example
./curl_commands.sh get_components
```

**Description**:
This script contains a collection of pre-configured curl commands for interacting with the QuickTARA API. It's useful for:
- Testing API endpoints
- Demonstrating API usage
- Troubleshooting API issues
- Creating and validating data

The script includes examples for all major API operations including component management, vulnerability assessment, and analysis.

## Adding New Utility Scripts

When adding new utility scripts to this directory:

1. Use descriptive filenames that indicate the script's purpose
2. Include thorough documentation within the script
3. Make the script executable if it's a shell script: `chmod +x script_name.sh`
4. Update this README.md with information about the new script

## Best Practices

1. Use utility scripts for repetitive tasks to ensure consistency
2. Document any environment-specific configurations required
3. Consider parametrizing scripts to make them more flexible
4. Share useful utilities with the team by adding them to this directory
