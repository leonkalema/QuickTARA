/**
 * User roles that match backend enum values exactly
 */
export enum UserRole {
  TOOL_ADMIN = 'tool_admin',
  ORG_ADMIN = 'org_admin', 
  RISK_MANAGER = 'risk_manager',
  COMPLIANCE_OFFICER = 'compliance_officer',
  PRODUCT_OWNER = 'product_owner',
  SECURITY_ENGINEER = 'security_engineer',
  TARA_ANALYST = 'tara_analyst',
  AUDITOR = 'auditor',
  VIEWER = 'viewer'
}

/**
 * Organization roles that match backend enum values exactly
 */
export enum OrgRole {
  TOOL_ADMIN = 'TOOL_ADMIN',
  ORG_ADMIN = 'ORG_ADMIN',
  RISK_MANAGER = 'RISK_MANAGER',
  COMPLIANCE_OFFICER = 'COMPLIANCE_OFFICER',
  PRODUCT_OWNER = 'PRODUCT_OWNER',
  SECURITY_ENGINEER = 'SECURITY_ENGINEER',
  TARA_ANALYST = 'TARA_ANALYST',
  AUDITOR = 'AUDITOR',
  VIEWER = 'VIEWER'
}

/**
 * Display labels for roles (for UI only)
 */
export const ROLE_LABELS: Record<UserRole, string> = {
  [UserRole.TOOL_ADMIN]: 'Tool Admin',
  [UserRole.ORG_ADMIN]: 'Organization Admin',
  [UserRole.RISK_MANAGER]: 'Risk Manager',
  [UserRole.COMPLIANCE_OFFICER]: 'Compliance Officer',
  [UserRole.PRODUCT_OWNER]: 'Product Owner',
  [UserRole.SECURITY_ENGINEER]: 'Security Engineer',
  [UserRole.TARA_ANALYST]: 'TARA Analyst',
  [UserRole.AUDITOR]: 'Auditor',
  [UserRole.VIEWER]: 'Viewer'
};

/**
 * Display labels for organization roles (for UI only)
 */
export const ORG_ROLE_LABELS: Record<OrgRole, string> = {
  [OrgRole.TOOL_ADMIN]: 'Tool Admin',
  [OrgRole.ORG_ADMIN]: 'Organization Admin',
  [OrgRole.RISK_MANAGER]: 'Risk Manager',
  [OrgRole.COMPLIANCE_OFFICER]: 'Compliance Officer',
  [OrgRole.PRODUCT_OWNER]: 'Product Owner',
  [OrgRole.SECURITY_ENGINEER]: 'Security Engineer',
  [OrgRole.TARA_ANALYST]: 'TARA Analyst',
  [OrgRole.AUDITOR]: 'Auditor',
  [OrgRole.VIEWER]: 'Viewer'
};

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
