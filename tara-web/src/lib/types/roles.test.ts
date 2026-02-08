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
    it('should have correct enum values matching backend (6 roles)', () => {
      expect(UserRole.TOOL_ADMIN).toBe('tool_admin');
      expect(UserRole.ORG_ADMIN).toBe('org_admin');
      expect(UserRole.ANALYST).toBe('analyst');
      expect(UserRole.RISK_MANAGER).toBe('risk_manager');
      expect(UserRole.AUDITOR).toBe('auditor');
      expect(UserRole.VIEWER).toBe('viewer');
    });
  });

  describe('OrgRole enum', () => {
    it('should have correct enum values matching backend (6 roles, lowercase)', () => {
      expect(OrgRole.TOOL_ADMIN).toBe('tool_admin');
      expect(OrgRole.ORG_ADMIN).toBe('org_admin');
      expect(OrgRole.ANALYST).toBe('analyst');
      expect(OrgRole.RISK_MANAGER).toBe('risk_manager');
      expect(OrgRole.AUDITOR).toBe('auditor');
      expect(OrgRole.VIEWER).toBe('viewer');
    });
  });

  describe('getAllUserRoles', () => {
    it('should return all user roles', () => {
      const roles = getAllUserRoles();
      expect(roles).toHaveLength(6);
      expect(roles).toContain(UserRole.TOOL_ADMIN);
      expect(roles).toContain(UserRole.ANALYST);
      expect(roles).toContain(UserRole.VIEWER);
    });
  });

  describe('getAllOrgRoles', () => {
    it('should return all organization roles', () => {
      const roles = getAllOrgRoles();
      expect(roles).toHaveLength(6);
      expect(roles).toContain(OrgRole.TOOL_ADMIN);
      expect(roles).toContain(OrgRole.ANALYST);
      expect(roles).toContain(OrgRole.VIEWER);
    });
  });

  describe('getUserRoleLabel', () => {
    it('should return correct display labels for user roles', () => {
      expect(getUserRoleLabel(UserRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getUserRoleLabel(UserRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getUserRoleLabel(UserRole.ANALYST)).toBe('Analyst');
      expect(getUserRoleLabel(UserRole.VIEWER)).toBe('Viewer');
    });

    it('should return the role value if no label exists', () => {
      const unknownRole = 'unknown_role' as UserRole;
      expect(getUserRoleLabel(unknownRole)).toBe('unknown_role');
    });
  });

  describe('getOrgRoleLabel', () => {
    it('should return correct display labels for org roles', () => {
      expect(getOrgRoleLabel(OrgRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getOrgRoleLabel(OrgRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getOrgRoleLabel(OrgRole.ANALYST)).toBe('Analyst');
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
        expect(role).toMatch(/^[a-z_]+$/);
        expect(role).not.toContain(' ');
        expect(role).not.toContain('-');
      });
    });

    it('org role values should match expected backend enum format (lowercase)', () => {
      const roles = getAllOrgRoles();
      roles.forEach(role => {
        expect(role).toMatch(/^[a-z_]+$/);
        expect(role).not.toContain(' ');
        expect(role).not.toContain('-');
      });
    });
  });
});
