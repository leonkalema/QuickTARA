import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { goto } from '$app/navigation';
import { 
  canViewUserManagement, 
  canManageOrganizations, 
  canManageSystemSettings,
  canManageOrgSettings,
  canManageRisk,
  canPerformTARA,
  canViewAuditLogs,
  isToolAdmin,
  isOrgAdmin
} from './permissions';

/**
 * Route guard functions to protect pages based on user roles
 */

/**
 * Redirect to unauthorized page
 */
function redirectToUnauthorized() {
  goto('/unauthorized');
}

/**
 * Redirect to login page
 */
function redirectToLogin() {
  goto('/login');
}

/**
 * Check if user is authenticated
 */
export function requireAuth(): boolean {
  const auth = get(authStore);
  if (!auth.isAuthenticated || !auth.user) {
    redirectToLogin();
    return false;
  }
  return true;
}

/**
 * Require Tool Admin role
 */
export function requireToolAdmin(): boolean {
  if (!requireAuth()) return false;
  
  if (!isToolAdmin()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require Organization Admin role or higher
 */
export function requireOrgAdmin(): boolean {
  if (!requireAuth()) return false;
  
  if (!isOrgAdmin()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require user management permissions
 */
export function requireUserManagement(): boolean {
  if (!requireAuth()) return false;
  
  if (!canViewUserManagement()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require organization management permissions
 */
export function requireOrgManagement(): boolean {
  if (!requireAuth()) return false;
  
  if (!canManageOrganizations()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require system settings management permissions
 */
export function requireSystemSettings(): boolean {
  if (!requireAuth()) return false;
  
  if (!canManageSystemSettings()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require organization settings management permissions
 */
export function requireOrgSettings(): boolean {
  if (!requireAuth()) return false;
  
  if (!canManageOrgSettings()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require risk management permissions
 */
export function requireRiskManagement(): boolean {
  if (!requireAuth()) return false;
  
  if (!canManageRisk()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require TARA analysis permissions
 */
export function requireTARAAccess(): boolean {
  if (!requireAuth()) return false;
  
  if (!canPerformTARA()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}

/**
 * Require audit log viewing permissions
 */
export function requireAuditAccess(): boolean {
  if (!requireAuth()) return false;
  
  if (!canViewAuditLogs()) {
    redirectToUnauthorized();
    return false;
  }
  return true;
}
