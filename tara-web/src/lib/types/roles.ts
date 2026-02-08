/**
 * User roles that match backend enum values exactly
 */
export enum UserRole {
  TOOL_ADMIN = 'tool_admin',      // System administration only
  ORG_ADMIN = 'org_admin',        // Full access within organization
  ANALYST = 'analyst',            // TARA analysis: assets, damage/threat scenarios
  RISK_MANAGER = 'risk_manager',  // Risk approvals and treatments
  AUDITOR = 'auditor',            // Read-only + compliance review
  VIEWER = 'viewer'               // Read-only access
}

/**
 * Organization/Department roles - excludes TOOL_ADMIN which is system-level only
 */
export enum OrgRole {
  ORG_ADMIN = 'org_admin',
  ANALYST = 'analyst',
  RISK_MANAGER = 'risk_manager',
  AUDITOR = 'auditor',
  VIEWER = 'viewer'
}

/**
 * Display labels for roles (for UI only)
 */
export const ROLE_LABELS: Record<UserRole, string> = {
  [UserRole.TOOL_ADMIN]: 'Tool Admin',
  [UserRole.ORG_ADMIN]: 'Department Admin',
  [UserRole.ANALYST]: 'Analyst',
  [UserRole.RISK_MANAGER]: 'Risk Manager',
  [UserRole.AUDITOR]: 'Auditor',
  [UserRole.VIEWER]: 'Viewer'
};

/**
 * Display labels for organization/department roles (for UI only)
 */
export const ORG_ROLE_LABELS: Record<OrgRole, string> = {
  [OrgRole.ORG_ADMIN]: 'Department Admin',
  [OrgRole.ANALYST]: 'Analyst',
  [OrgRole.RISK_MANAGER]: 'Risk Manager',
  [OrgRole.AUDITOR]: 'Auditor',
  [OrgRole.VIEWER]: 'Viewer'
};

/**
 * Normalize a role string to lowercase for consistent comparison
 */
export function normalizeRole(role: string): string {
  return role?.toLowerCase() ?? '';
}

/**
 * Get all available user roles as array
 */
export function getAllUserRoles(): UserRole[] {
  return Object.values(UserRole);
}

/**
 * Get all available organization roles as array
 */
export function getAllOrgRoles(): OrgRole[] {
  return Object.values(OrgRole);
}

/**
 * Get display label for a user role
 */
export function getUserRoleLabel(role: UserRole): string {
  return ROLE_LABELS[role] || role;
}

/**
 * Get display label for an organization role
 */
export function getOrgRoleLabel(role: OrgRole): string {
  return ORG_ROLE_LABELS[role] || role;
}
