# Final Fix Instructions for QuickTARA Vulnerability Setup

## Quick Solution

Run these commands in order:

```bash
# 1. First, run the debug script to see what's wrong
python debug_current_state.py

# 2. If you see model conflicts, run the complete fix
python fix_vulnerability_complete.py

# 3. Finally, start the application
python quicktara_web.py --debug
```

## Manual Fix (if needed)

If the above doesn't work, here are the exact files that need to be fixed:

### 1. Remove duplicate Vulnerability class from db/base.py

There's a second `Vulnerability` class at the end of the file that needs to be removed. Keep only the first one.

### 2. Update vulnerability routes to use correct imports

The file `api/routes/vulnerability.py` should import from `api.deps.db` not `api.deps.database`.

### 3. Ensure model fields match

The vulnerability model fields need to match between the database model, Pydantic model, and service.

## Verification

After fixing, you should be able to:

1. Start the application without errors
2. Access the API docs at http://localhost:8080/docs
3. See vulnerability endpoints in the API documentation

## If you still get errors

1. Delete the database file: `rm quicktara.db`
2. Run: `python quicktara_web.py --initialize-db`
3. Start the app: `python quicktara_web.py --debug`

The issue is mainly about a duplicate class definition that needs to be removed.
