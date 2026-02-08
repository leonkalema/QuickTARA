"""
Product-Context RBAC - Permissions based on user's role in the product's department
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from ..models.user import User, UserRole, user_organizations


def get_user_role_in_product_org(db: Session, user_id: str, product_org_id: str) -> Optional[str]:
    """Get user's role in a product's organization"""
    if not product_org_id:
        return None
    
    membership = db.execute(
        user_organizations.select().where(
            and_(
                user_organizations.c.user_id == user_id,
                user_organizations.c.organization_id == product_org_id
            )
        )
    ).first()
    
    return membership.role.lower() if membership and membership.role else None


def can_view_product(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can view a product (any role in the product's org)"""
    if user.is_superuser:
        return True
    if not product_org_id:
        return True  # Products without org are visible to all authenticated users
    
    role = get_user_role_in_product_org(db, user.user_id, product_org_id)
    return role is not None


def can_edit_product(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can edit a product (analyst or higher in the product's org)"""
    if user.is_superuser:
        return True
    if not product_org_id:
        return True  # Products without org can be edited by authenticated users
    
    role = get_user_role_in_product_org(db, user.user_id, product_org_id)
    if not role:
        return False
    
    # Roles that can edit: org_admin, analyst, risk_manager
    edit_roles = ['org_admin', 'analyst', 'risk_manager']
    return role in edit_roles


def can_delete_product(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can delete a product (org_admin only in the product's org)"""
    if user.is_superuser:
        return True
    if not product_org_id:
        return False  # Only superusers can delete unassigned products
    
    role = get_user_role_in_product_org(db, user.user_id, product_org_id)
    if not role:
        return False
    
    # Only org_admin can delete
    return role == 'org_admin'


def can_manage_assets(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can manage assets (analyst or higher)"""
    return can_edit_product(db, user, product_org_id)


def can_manage_scenarios(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can manage damage/threat scenarios (analyst or higher)"""
    return can_edit_product(db, user, product_org_id)


def can_approve_risks(db: Session, user: User, product_org_id: Optional[str]) -> bool:
    """Check if user can approve/reject risks (risk_manager or org_admin)"""
    if user.is_superuser:
        return True
    if not product_org_id:
        return False
    
    role = get_user_role_in_product_org(db, user.user_id, product_org_id)
    if not role:
        return False
    
    approve_roles = ['org_admin', 'risk_manager']
    return role in approve_roles


def get_product_permissions(db: Session, user: User, product_org_id: Optional[str]) -> dict:
    """Get all permissions for a user on a specific product"""
    return {
        'can_view': can_view_product(db, user, product_org_id),
        'can_edit': can_edit_product(db, user, product_org_id),
        'can_delete': can_delete_product(db, user, product_org_id),
        'can_manage_assets': can_manage_assets(db, user, product_org_id),
        'can_manage_scenarios': can_manage_scenarios(db, user, product_org_id),
        'can_approve_risks': can_approve_risks(db, user, product_org_id),
        'role': get_user_role_in_product_org(db, user.user_id, product_org_id) if product_org_id else None
    }
