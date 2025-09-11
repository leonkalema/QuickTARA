import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { 
  hasRole, 
  hasAnyRole, 
  isToolAdmin, 
  isOrgAdmin, 
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
} from './permissions';
import { UserRole } from '$lib/types/roles';

// Mock the auth store
vi.mock('$lib/stores/auth', () => ({
  authStore: {
    subscribe: vi.fn(),
    // Mock store will be set up in tests
  }
}));

// Mock svelte/store
vi.mock('svelte/store', () => ({
  get: vi.fn()
}));

const mockGet = vi.mocked(get);

describe('Permission Utils', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('hasRole', () => {
    it('should return false for unauthenticated user', () => {
      mockGet.mockReturnValue({
        user: null,
        isAuthenticated: false
      });

      expect(hasRole(UserRole.TARA_ANALYST)).toBe(false);
    });

    it('should return false for superuser without matching role', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: true, organizations: [] },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.TARA_ANALYST)).toBe(false);
      expect(hasRole(UserRole.VIEWER)).toBe(false);
    });

    it('should return true for tool admin with specific role', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: 'tool_admin' }] // Backend uses lowercase
        },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.TOOL_ADMIN)).toBe(true);
      expect(hasRole(UserRole.VIEWER)).toBe(false);
    });

    it('should return true if user has the specific role in any organization', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [
            { role: 'tara_analyst' }, // Backend uses lowercase
            { role: 'viewer' }
          ]
        },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.TARA_ANALYST)).toBe(true);
      expect(hasRole(UserRole.VIEWER)).toBe(true);
      expect(hasRole(UserRole.ORG_ADMIN)).toBe(false);
    });

    it('should return false if user does not have the role', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.VIEWER }]
        },
        isAuthenticated: true
      });

      expect(hasRole(UserRole.ORG_ADMIN)).toBe(false);
    });
  });

  describe('hasAnyRole', () => {
    it('should return true if user has any of the specified roles', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [
            { role: 'tara_analyst' },
            { role: 'viewer' }
          ]
        },
        isAuthenticated: true
      });

      expect(hasAnyRole([UserRole.TARA_ANALYST, UserRole.ORG_ADMIN])).toBe(true);
      expect(hasAnyRole([UserRole.RISK_MANAGER, UserRole.COMPLIANCE_OFFICER])).toBe(false);
    });
  });

  describe('isToolAdmin', () => {
    it('should return true for superuser', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: true },
        isAuthenticated: true
      });

      expect(isToolAdmin()).toBe(true);
    });

    it('should return false for non-superuser', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: false },
        isAuthenticated: true
      });

      expect(isToolAdmin()).toBe(false);
    });

    it('should return false for null user', () => {
      mockGet.mockReturnValue({
        user: null,
        isAuthenticated: false
      });

      expect(isToolAdmin()).toBe(false);
    });
  });

  describe('isOrgAdmin', () => {
    it('should return true for tool admin', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: true, organizations: [] },
        isAuthenticated: true
      });

      expect(isOrgAdmin()).toBe(true);
    });

    it('should return true for org admin role', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: 'org_admin' }]
        },
        isAuthenticated: true
      });

      expect(isOrgAdmin()).toBe(true);
    });

    it('should return false for other roles', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.TARA_ANALYST }]
        },
        isAuthenticated: true
      });

      expect(isOrgAdmin()).toBe(false);
    });
  });

  describe('canManageUsers', () => {
    it('should return true for tool admin', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: true, organizations: [] },
        isAuthenticated: true
      });

      expect(canManageUsers()).toBe(true);
    });

    it('should return true for org admin', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: 'org_admin' }]
        },
        isAuthenticated: true
      });

      expect(canManageUsers()).toBe(true);
    });

    it('should return false for other roles', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.TARA_ANALYST }]
        },
        isAuthenticated: true
      });

      expect(canManageUsers()).toBe(false);
    });
  });

  describe('canManageOrganizations', () => {
    it('should return true only for tool admin', () => {
      mockGet.mockReturnValue({
        user: { is_superuser: true, organizations: [] },
        isAuthenticated: true
      });

      expect(canManageOrganizations()).toBe(true);
    });

    it('should return false for org admin', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.ORG_ADMIN }]
        },
        isAuthenticated: true
      });

      expect(canManageOrganizations()).toBe(false);
    });
  });

  describe('User Management Permissions', () => {
    it('should have consistent user management permissions', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: 'org_admin' }]
        },
        isAuthenticated: true
      });

      expect(canViewUserManagement()).toBe(true);
      expect(canCreateUsers()).toBe(true);
      expect(canEditUsers()).toBe(true);
      expect(canDeleteUsers()).toBe(true);
    });
  });

  describe('canPerformTARA', () => {
    it('should return true for TARA-related roles', () => {
      const taraRoles = [
        UserRole.TOOL_ADMIN,
        UserRole.ORG_ADMIN,
        UserRole.RISK_MANAGER,
        UserRole.SECURITY_ENGINEER,
        UserRole.TARA_ANALYST
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
    });

    it('should return false for non-TARA roles', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: UserRole.VIEWER }]
        },
        isAuthenticated: true
      });

      expect(canPerformTARA()).toBe(false);
    });
  });

  describe('isReadOnly', () => {
    it('should return true only for viewer role without other permissions', () => {
      mockGet.mockReturnValue({
        user: {
          is_superuser: false,
          organizations: [{ role: 'viewer' }]
        },
        isAuthenticated: true
      });

      expect(isReadOnly()).toBe(true);
    });

    it('should return false for users with higher permissions', () => {
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
});
