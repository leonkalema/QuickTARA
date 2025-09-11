import { describe, it, expect, beforeEach, vi } from 'vitest';
import { UserRole } from '$lib/types/roles';

// Mock the authStore
vi.mock('svelte/store', () => ({
  get: vi.fn()
}));

vi.mock('$lib/stores/auth', () => ({
  authStore: {}
}));

import { 
  hasRole, 
  isToolAdmin, 
  isOrgAdmin, 
  getPrimaryRole, 
  getUserRoleDisplay,
  hasAnyRole,
  canManageUsers,
  canManageOrganizations,
  canViewUserManagement,
  canCreateUsers,
  canEditUsers,
  canDeleteUsers,
  canManageSystemSettings,
  canManageOrgSettings,
  canManageRisk,
  canPerformTARA,
  canViewAuditLogs,
  isReadOnly
} from '$lib/utils/permissions';

describe('Centralized Role Management', () => {
  let mockGet: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockGet = vi.mocked(await import('svelte/store')).get;
  });

  describe('Core Role Functions', () => {
    it('should provide centralized role checking', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.ORG_ADMIN }]
        },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.ORG_ADMIN)).toBe(true);
      expect(hasRole(UserRole.VIEWER)).toBe(false);
      expect(isOrgAdmin()).toBe(true);
      expect(isToolAdmin()).toBe(false);
    });

    it('should handle multiple role checks consistently', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: true,
          organizations: [{ role: UserRole.TOOL_ADMIN }]
        },
        isAuthenticated: true
      });

      expect(isToolAdmin()).toBe(true);
      expect(isOrgAdmin()).toBe(true); // Tool admin includes org admin
      expect(hasAnyRole([UserRole.TOOL_ADMIN, UserRole.VIEWER])).toBe(true);
    });

    it('should provide consistent primary role information', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [
            { role: UserRole.TARA_ANALYST },
            { role: UserRole.VIEWER }
          ]
        },
        isAuthenticated: true
      });

      expect(getPrimaryRole()).toBe(UserRole.TARA_ANALYST);
      expect(getUserRoleDisplay()).toBe('TARA Analyst');
    });
  });

  describe('Permission Consistency', () => {
    it('should have consistent user management permissions', () => {
      const testCases = [
        { role: UserRole.TOOL_ADMIN, canManage: true },
        { role: UserRole.ORG_ADMIN, canManage: true },
        { role: UserRole.TARA_ANALYST, canManage: false },
        { role: UserRole.VIEWER, canManage: false }
      ];

      testCases.forEach(({ role, canManage }) => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: role === UserRole.TOOL_ADMIN,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canManageUsers()).toBe(canManage);
        expect(canViewUserManagement()).toBe(canManage);
        expect(canCreateUsers()).toBe(canManage);
        expect(canEditUsers()).toBe(canManage);
        expect(canDeleteUsers()).toBe(canManage);
      });
    });

    it('should have consistent organization management permissions', () => {
      const testCases = [
        { role: UserRole.TOOL_ADMIN, canManage: true },
        { role: UserRole.ORG_ADMIN, canManage: false },
        { role: UserRole.TARA_ANALYST, canManage: false }
      ];

      testCases.forEach(({ role, canManage }) => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: role === UserRole.TOOL_ADMIN,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canManageOrganizations()).toBe(canManage);
      });
    });

    it('should have consistent system settings permissions', () => {
      const testCases = [
        { role: UserRole.TOOL_ADMIN, canManage: true },
        { role: UserRole.ORG_ADMIN, canManage: false },
        { role: UserRole.TARA_ANALYST, canManage: false }
      ];

      testCases.forEach(({ role, canManage }) => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: role === UserRole.TOOL_ADMIN,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canManageSystemSettings()).toBe(canManage);
      });
    });

    it('should have consistent TARA permissions', () => {
      const taraRoles = [
        UserRole.TOOL_ADMIN,
        UserRole.ORG_ADMIN,
        UserRole.RISK_MANAGER,
        UserRole.SECURITY_ENGINEER,
        UserRole.TARA_ANALYST
      ];

      const nonTaraRoles = [
        UserRole.COMPLIANCE_OFFICER,
        UserRole.PRODUCT_OWNER,
        UserRole.AUDITOR,
        UserRole.VIEWER
      ];

      taraRoles.forEach(role => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: role === UserRole.TOOL_ADMIN,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canPerformTARA()).toBe(true);
      });

      nonTaraRoles.forEach(role => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: false,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canPerformTARA()).toBe(false);
      });
    });

    it('should have consistent risk management permissions', () => {
      const riskRoles = [
        UserRole.TOOL_ADMIN,
        UserRole.ORG_ADMIN,
        UserRole.RISK_MANAGER
      ];

      const nonRiskRoles = [
        UserRole.COMPLIANCE_OFFICER,
        UserRole.PRODUCT_OWNER,
        UserRole.SECURITY_ENGINEER,
        UserRole.TARA_ANALYST,
        UserRole.AUDITOR,
        UserRole.VIEWER
      ];

      riskRoles.forEach(role => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: role === UserRole.TOOL_ADMIN,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canManageRisk()).toBe(true);
      });

      nonRiskRoles.forEach(role => {
        mockGet.mockReturnValue({
          user: {
            is_superuser: false,
            organizations: [{ role }]
          },
          isAuthenticated: true
        });

        expect(canManageRisk()).toBe(false);
      });
    });

    it('should correctly identify read-only users', () => {
      // Viewer with no other roles should be read-only
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.VIEWER }]
        },
        isAuthenticated: true
      });

      expect(isReadOnly()).toBe(true);

      // TARA Analyst should not be read-only
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.TARA_ANALYST }]
        },
        isAuthenticated: true
      });

      expect(isReadOnly()).toBe(false);
    });
  });

  describe('Edge Cases', () => {
    it('should handle unauthenticated users consistently', () => {
      mockGet.mockReturnValue({
        user: null,
        isAuthenticated: false
      });

      expect(hasRole(UserRole.TOOL_ADMIN)).toBe(false);
      expect(isToolAdmin()).toBe(false);
      expect(isOrgAdmin()).toBe(false);
      expect(canManageUsers()).toBe(false);
      expect(canPerformTARA()).toBe(false);
      expect(getPrimaryRole()).toBe(null);
      expect(getUserRoleDisplay()).toBe('No role assigned');
    });

    it('should handle users with no organizations', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: []
        },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.TOOL_ADMIN)).toBe(false);
      expect(isOrgAdmin()).toBe(false);
      expect(canManageUsers()).toBe(false);
      expect(getPrimaryRole()).toBe(null);
    });

    it('should handle superuser flag correctly', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: true,
          organizations: [{ role: UserRole.VIEWER }]
        },
        isAuthenticated: true
      });

      expect(isToolAdmin()).toBe(true); // Superuser flag takes precedence
      expect(canManageSystemSettings()).toBe(true);
      expect(canManageOrganizations()).toBe(true);
    });
  });
});
