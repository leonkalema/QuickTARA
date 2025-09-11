import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { UserRole, getUserRoleLabel } from '$lib/types/roles';

/**
 * Permission utility functions for role-based access control
 */

/**
 * Check if user has a specific role in any organization
 */
export function hasRole(role: UserRole): boolean {
  const auth = get(authStore);
  
  if (!auth.isAuthenticated || !auth.user) {
    return false;
  }

  // Convert backend role format (should be lowercase) to match UserRole enums
  const normalizeRole = (backendRole: string): string => {
    return backendRole.toLowerCase();
  };
  // Check if user has the specific role in any organization
  return auth.user.organizations?.some(org => normalizeRole(org.role) === role) || false;
}

/**
 * Check if current user has any of the specified roles
 */
export function hasAnyRole(roles: UserRole[]): boolean {
  return roles.some(role => hasRole(role));
}

/**
 * Check if user has Tool Admin role (highest privilege)
 */
export function isToolAdmin(): boolean {
  const auth = get(authStore);
  return auth.user?.is_superuser || hasRole(UserRole.TOOL_ADMIN);
}

/**
 * Check if user has Organization Admin role or higher
 */
export function isOrgAdmin(): boolean {
  return isToolAdmin() || hasRole(UserRole.ORG_ADMIN);
}

/**
 * Get user's primary role (first organization role)
 */
export function getPrimaryRole(): UserRole | null {
  const auth = get(authStore);
  
  if (!auth.isAuthenticated || !auth.user?.organizations?.length) {
    return null;
  }

  // Convert backend role format (lowercase) to frontend format (uppercase)
  const backendRole = auth.user.organizations[0]?.role;
  return backendRole ? backendRole.toUpperCase() as UserRole : null;
}

/**
 * Get user's role display label
 */
export function getUserRoleDisplay(): string {
  const role = getPrimaryRole();
  return role ? getUserRoleLabel(role) : 'No role assigned';
}

/**
 * Check if current user can manage users (Tool Admin or Org Admin)
 */
export function canManageUsers(): boolean {
  return isToolAdmin() || isOrgAdmin();
}

/**
 * Check if current user can manage organizations (Tool Admin only)
 */
export function canManageOrganizations(): boolean {
  return isToolAdmin();
}

/**
 * Check if current user can view user management pages
 */
export function canViewUserManagement(): boolean {
  return canManageUsers();
}

/**
 * Check if current user can create users
 */
export function canCreateUsers(): boolean {
  return canManageUsers();
}

/**
 * Check if current user can edit users
 */
export function canEditUsers(): boolean {
  return canManageUsers();
}

/**
 * Check if current user can delete users
 */
export function canDeleteUsers(): boolean {
  return canManageUsers();
}

/**
 * Check if current user can manage system settings
 */
export function canManageSystemSettings(): boolean {
  return isToolAdmin();
}

/**
 * Check if current user can manage organization settings
 */
export function canManageOrgSettings(): boolean {
  return isOrgAdmin();
}

/**
 * Check if current user can perform risk management tasks
 */
export function canManageRisk(): boolean {
  return hasAnyRole([
    UserRole.TOOL_ADMIN,
    UserRole.ORG_ADMIN,
    UserRole.RISK_MANAGER
  ]);
}

/**
 * Check if current user can perform TARA analysis
 */
export function canPerformTARA(): boolean {
  return hasAnyRole([
    UserRole.TOOL_ADMIN,
    UserRole.ORG_ADMIN,
    UserRole.RISK_MANAGER,
    UserRole.SECURITY_ENGINEER,
    UserRole.TARA_ANALYST
  ]);
}

/**
 * Check if current user can view audit logs
 */
export function canViewAuditLogs(): boolean {
  return hasAnyRole([
    UserRole.TOOL_ADMIN,
    UserRole.ORG_ADMIN,
    UserRole.COMPLIANCE_OFFICER,
    UserRole.AUDITOR
  ]);
}

/**
 * Check if current user has read-only access
 */
export function isReadOnly(): boolean {
  return hasRole(UserRole.VIEWER) && !hasAnyRole([
    UserRole.TOOL_ADMIN,
    UserRole.ORG_ADMIN,
    UserRole.RISK_MANAGER,
    UserRole.COMPLIANCE_OFFICER,
    UserRole.PRODUCT_OWNER,
    UserRole.SECURITY_ENGINEER,
    UserRole.TARA_ANALYST,
    UserRole.AUDITOR
  ]);
}
