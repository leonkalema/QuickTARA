"""
Workflow RBAC — role-based access control for approval workflow transitions.

Maps each workflow transition to required permissions and enforces
separation of duties (submitter ≠ approver).
"""
from typing import List
from fastapi import HTTPException, status
from api.models.user import User, UserRole, ROLE_PERMISSIONS
from api.auth.dependencies import get_user_roles


# Permission required for each transition target state
TRANSITION_PERMISSION: dict[str, str] = {
    "draft": "workflows:submit",
    "review": "workflows:submit",
    "approved": "workflows:approve",
    "released": "workflows:release",
}

CREATE_PERMISSION = "workflows:create"
SIGNOFF_PERMISSION = "workflows:signoff"
READ_PERMISSION = "workflows:read"


def _user_has_permission(user: User, permission: str) -> bool:
    """Check if a user has a specific workflow permission."""
    if user.is_superuser:
        return True
    roles = get_user_roles(user)
    for role in roles:
        perms = ROLE_PERMISSIONS.get(role, [])
        if "workflows:*" in perms or permission in perms:
            return True
    return False


def assert_can_create_workflow(user: User) -> None:
    """Raise 403 if the user cannot create workflows."""
    if not _user_has_permission(user, CREATE_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create workflows. "
                   "Required role: analyst, org_admin, or tool_admin.",
        )


def assert_can_transition(
    user: User,
    target_state: str,
    workflow_created_by: str,
) -> None:
    """Raise 403 if the user cannot perform this transition.

    Also enforces separation of duties: the person who submitted
    for review cannot be the one who approves.
    """
    perm = TRANSITION_PERMISSION.get(target_state)
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown target state: {target_state}",
        )
    if not _user_has_permission(user, perm):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to transition to '{target_state}'. "
                   f"Required permission: {perm}.",
        )
    # Separation of duties: submitter cannot approve their own work
    if target_state == "approved" and user.email == workflow_created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Separation of duties: you cannot approve a workflow "
                   "you submitted. A different reviewer must approve.",
        )


def assert_can_signoff(user: User) -> None:
    """Raise 403 if the user cannot add sign-offs."""
    if not _user_has_permission(user, SIGNOFF_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add sign-offs. "
                   "Required role: risk_manager, auditor, or org_admin.",
        )


def get_allowed_transitions_for_user(
    user: User,
    current_state: str,
    workflow_created_by: str,
) -> List[str]:
    """Return the list of target states this user is allowed to transition to."""
    from db.audit_models import VALID_TRANSITIONS

    allowed_by_state = VALID_TRANSITIONS.get(current_state, [])
    result: List[str] = []
    for target in allowed_by_state:
        perm = TRANSITION_PERMISSION.get(target)
        if not perm:
            continue
        if not _user_has_permission(user, perm):
            continue
        # Separation of duties check
        if target == "approved" and user.email == workflow_created_by:
            continue
        result.append(target)
    return result
