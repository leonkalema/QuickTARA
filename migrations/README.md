# QuickTARA Database Migrations

This directory contains all database migration scripts for the QuickTARA project.

## Migration Workflow

1. **Creating a New Migration**
   - Name your migration script descriptively with a prefix indicating what it does
   - Example: `add_[feature]_table.py`, `update_[table]_schema.py`
   - Include both upgrade and downgrade functionality when possible

2. **Structure of Migration Scripts**
   - Each script should be self-contained and focused on a specific change
   - Include appropriate error handling and logging
   - Document the purpose and changes in comments

3. **Running Migrations**
   - Use the main migration runner: `python migrations/db_migrate.py`
   - For specific migrations: `python migrations/[specific_script].py`

4. **Migration Order**
   The scripts should generally be run in this order for a fresh installation:

   1. `db_create_vulnerability_tables.py` - Creates initial vulnerability schema
   2. `add_scope_id_column.py` - Adds scope ID relationship
   3. `add_risk_framework_table.py` - Adds risk framework tables
   4. `add_vulnerability_data.py` - Populates vulnerability data
   5. `attack_path_analyses_table.sql` - SQL script for attack path analysis tables

## Guidelines

- Always back up the database before running migrations
- Test migrations on a development environment before production
- Keep migrations backward compatible when possible
- Update the QuickTARA documentation when schema changes significantly

## Troubleshooting

If you encounter issues with migrations:

1. Check the logs for specific errors
2. Verify database permissions
3. For SQLite conflicts, ensure no other processes have the database locked
4. For complex migrations, consider breaking them into smaller steps
