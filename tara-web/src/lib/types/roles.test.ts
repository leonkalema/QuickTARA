import { describe, it, expect } from 'vitest';
import { 
  UserRole, 
  OrgRole, 
  getAllUserRoles, 
  getAllOrgRoles, 
  getUserRoleLabel, 
  getOrgRoleLabel,
  ROLE_LABELS,
  ORG_ROLE_LABELS
} from './roles';

describe('Role Types and Utilities', () => {
  describe('UserRole enum', () => {
    it('should have correct enum values matching backend', () => {
      expect(UserRole.TOOL_ADMIN).toBe('tool_admin');
      expect(UserRole.ORG_ADMIN).toBe('org_admin');
      expect(UserRole.RISK_MANAGER).toBe('risk_manager');
      expect(UserRole.COMPLIANCE_OFFICER).toBe('compliance_officer');
      expect(UserRole.PRODUCT_OWNER).toBe('product_owner');
      expect(UserRole.SECURITY_ENGINEER).toBe('security_engineer');
      expect(UserRole.TARA_ANALYST).toBe('tara_analyst');
      expect(UserRole.AUDITOR).toBe('auditor');
      expect(UserRole.VIEWER).toBe('viewer');
    });
  });

  describe('OrgRole enum', () => {
    it('should have correct enum values matching backend', () => {
      expect(OrgRole.TOOL_ADMIN).toBe('TOOL_ADMIN');
      expect(OrgRole.ORG_ADMIN).toBe('ORG_ADMIN');
      expect(OrgRole.RISK_MANAGER).toBe('RISK_MANAGER');
      expect(OrgRole.COMPLIANCE_OFFICER).toBe('COMPLIANCE_OFFICER');
      expect(OrgRole.PRODUCT_OWNER).toBe('PRODUCT_OWNER');
      expect(OrgRole.SECURITY_ENGINEER).toBe('SECURITY_ENGINEER');
      expect(OrgRole.TARA_ANALYST).toBe('TARA_ANALYST');
      expect(OrgRole.AUDITOR).toBe('AUDITOR');
      expect(OrgRole.VIEWER).toBe('VIEWER');
    });
  });

  describe('getAllUserRoles', () => {
    it('should return all user roles', () => {
      const roles = getAllUserRoles();
      expect(roles).toHaveLength(9);
      expect(roles).toContain(UserRole.TOOL_ADMIN);
      expect(roles).toContain(UserRole.TARA_ANALYST);
      expect(roles).toContain(UserRole.VIEWER);
    });
  });

  describe('getAllOrgRoles', () => {
    it('should return all organization roles', () => {
      const roles = getAllOrgRoles();
      expect(roles).toHaveLength(9);
      expect(roles).toContain(OrgRole.TOOL_ADMIN);
      expect(roles).toContain(OrgRole.TARA_ANALYST);
      expect(roles).toContain(OrgRole.VIEWER);
    });
  });

  describe('getUserRoleLabel', () => {
    it('should return correct display labels for user roles', () => {
      expect(getUserRoleLabel(UserRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getUserRoleLabel(UserRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getUserRoleLabel(UserRole.TARA_ANALYST)).toBe('TARA Analyst');
      expect(getUserRoleLabel(UserRole.VIEWER)).toBe('Viewer');
    });

    it('should return the role value if no label exists', () => {
      // This tests the fallback behavior
      const unknownRole = 'unknown_role' as UserRole;
      expect(getUserRoleLabel(unknownRole)).toBe('unknown_role');
    });
  });

  describe('getOrgRoleLabel', () => {
    it('should return correct display labels for org roles', () => {
      expect(getOrgRoleLabel(OrgRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getOrgRoleLabel(OrgRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getOrgRoleLabel(OrgRole.TARA_ANALYST)).toBe('TARA Analyst');
      expect(getOrgRoleLabel(OrgRole.VIEWER)).toBe('Viewer');
    });
  });

  describe('Role Labels Mapping', () => {
    it('should have labels for all user roles', () => {
      const allRoles = getAllUserRoles();
      allRoles.forEach(role => {
        expect(ROLE_LABELS[role]).toBeDefined();
        expect(typeof ROLE_LABELS[role]).toBe('string');
        expect(ROLE_LABELS[role].length).toBeGreaterThan(0);
      });
    });

    it('should have labels for all org roles', () => {
      const allRoles = getAllOrgRoles();
      allRoles.forEach(role => {
        expect(ORG_ROLE_LABELS[role]).toBeDefined();
        expect(typeof ORG_ROLE_LABELS[role]).toBe('string');
        expect(ORG_ROLE_LABELS[role].length).toBeGreaterThan(0);
      });
    });
  });

  describe('Backend Compatibility', () => {
    it('user role values should match expected backend enum format', () => {
      const roles = getAllUserRoles();
      roles.forEach(role => {
        // Backend enum values are lowercase with underscores
        expect(role).toMatch(/^[a-z_]+$/);
        expect(role).not.toContain(' ');
        expect(role).not.toContain('-');
      });
    });

    it('org role values should match expected backend enum format', () => {
      const roles = getAllOrgRoles();
      roles.forEach(role => {
        // Backend org enum values are uppercase with underscores
        expect(role).toMatch(/^[A-Z_]+$/);
        expect(role).not.toContain(' ');
        expect(role).not.toContain('-');
      });
    });
  });
});
