# QuickTARA Database Layer

This directory contains the database layer components for QuickTARA.

## Components

- `base.py`: SQLAlchemy model definitions
- `session.py`: Database connection and session handling
- `migrations/`: Alembic database migrations

## Database Models

The database models defined in `base.py` include:

- `Component`: Stores component information (ECUs, sensors, etc.)
- `Analysis`: Stores analysis results metadata
- `ComponentAnalysis`: Stores detailed analysis results for each component
- `Report`: Stores generated reports
- `ReviewDecision`: Stores risk review decisions

## Database Configuration

The database connection is configured through the `get_database_url` function in `session.py`. The database type and connection parameters can be specified in the configuration file.

Supported database types:
- SQLite (default)
- PostgreSQL
- MySQL

## Using Database Migrations

Database migrations are managed with Alembic. The following commands are available through the `db_migrate.py` script:

```bash
# Create a new migration (with auto-detection of changes)
python db_migrate.py create "Description of changes"

# Apply all pending migrations
python db_migrate.py upgrade

# Downgrade to a previous revision
python db_migrate.py downgrade

# Show migration history
python db_migrate.py history

# Show current revision
python db_migrate.py current
```

For more advanced Alembic commands, you can use Alembic directly:

```bash
# Create a blank migration
alembic revision -m "Description of changes"

# Create a migration with auto-detection of changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations up to a specific revision
alembic upgrade <revision_id>
```

## Migrating Review Data

When transitioning from file-based storage to database storage for review decisions, you can use the `db/migrate_review_data.py` script:

```bash
python db/migrate_review_data.py
```

This script will:
1. Find all review decision JSON files in the `uploads/reviews` directory
2. Create corresponding entries in the `review_decisions` table
3. Report the number of migrated decisions

## Adding New Models

When adding new models:

1. Define your model in `db/base.py` inheriting from `Base`
2. Import your model in `db/migrations/env.py`
3. Generate a new migration using:
   ```bash
   python db_migrate.py create "Add new model"
   ```
4. Review the generated migration script
5. Apply the migration:
   ```bash
   python db_migrate.py upgrade
   ```
