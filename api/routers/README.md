# Legacy Routers Directory

This directory previously contained the attack_path.py router which has now been moved to the standard routes directory for better API organization and consistency.

The attack path endpoints can now be accessed at:
- `/api/attack-paths` - List and create attack paths
- `/api/attack-paths/{path_id}` - Get a specific attack path
- `/api/attack-paths/chains` - List attack chains
- `/api/attack-paths/chains/{chain_id}` - Get a specific attack chain

This change was made to standardize the API structure and make the codebase more maintainable.
