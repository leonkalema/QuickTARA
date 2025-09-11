import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { goto } from '$app/navigation';
import {
  requireAuth,
  requireToolAdmin,
  requireOrgAdmin,
  requireUserManagement,
  requireOrgManagement,
  requireSystemSettings,
  requireOrgSettings,
  requireRiskManagement,
  requireTARAAccess,
  requireAuditAccess
} from './routeGuards';
import { UserRole } from '$lib/types/roles';

// Mock dependencies
vi.mock('svelte/store', () => ({
  get: vi.fn(),
  writable: vi.fn(() => ({
    subscribe: vi.fn(),
    set: vi.fn(),
    update: vi.fn()
  })),
  readable: vi.fn(),
  derived: vi.fn()
}));

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('./permissions', () => ({
  canViewUserManagement: vi.fn(),
  canManageOrganizations: vi.fn(),
  canManageSystemSettings: vi.fn(),
  canManageOrgSettings: vi.fn(),
  canManageRisk: vi.fn(),
  canPerformTARA: vi.fn(),
  canViewAuditLogs: vi.fn(),
  isToolAdmin: vi.fn(),
  isOrgAdmin: vi.fn()
}));

const mockGet = vi.mocked(get);
const mockGoto = vi.mocked(goto);

// Import mocked permissions
import * as permissions from './permissions';
const mockPermissions = vi.mocked(permissions);

describe('Route Guards', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('requireAuth', () => {
    it('should return true for authenticated user', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });

      expect(requireAuth()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to login for unauthenticated user', () => {
      mockGet.mockReturnValue({
        isAuthenticated: false,
        user: null
      });

      expect(requireAuth()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/login');
    });

    it('should redirect to login for missing user', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: null
      });

      expect(requireAuth()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/login');
    });
  });

  describe('requireToolAdmin', () => {
    it('should return true for tool admin', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.isToolAdmin.mockReturnValue(true);

      expect(requireToolAdmin()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized for non-tool admin', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.isToolAdmin.mockReturnValue(false);

      expect(requireToolAdmin()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });

    it('should redirect to login for unauthenticated user', () => {
      mockGet.mockReturnValue({
        isAuthenticated: false,
        user: null
      });

      expect(requireToolAdmin()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/login');
    });
  });

  describe('requireOrgAdmin', () => {
    it('should return true for org admin', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.isOrgAdmin.mockReturnValue(true);

      expect(requireOrgAdmin()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized for non-org admin', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.isOrgAdmin.mockReturnValue(false);

      expect(requireOrgAdmin()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });
  });

  describe('requireUserManagement', () => {
    it('should return true when user can manage users', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canViewUserManagement.mockReturnValue(true);

      expect(requireUserManagement()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized when user cannot manage users', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canViewUserManagement.mockReturnValue(false);

      expect(requireUserManagement()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });
  });

  describe('requireOrgManagement', () => {
    it('should return true when user can manage organizations', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canManageOrganizations.mockReturnValue(true);

      expect(requireOrgManagement()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized when user cannot manage organizations', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canManageOrganizations.mockReturnValue(false);

      expect(requireOrgManagement()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });
  });

  describe('requireSystemSettings', () => {
    it('should return true when user can manage system settings', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canManageSystemSettings.mockReturnValue(true);

      expect(requireSystemSettings()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized when user cannot manage system settings', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canManageSystemSettings.mockReturnValue(false);

      expect(requireSystemSettings()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });
  });

  describe('requireTARAAccess', () => {
    it('should return true when user can perform TARA', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canPerformTARA.mockReturnValue(true);

      expect(requireTARAAccess()).toBe(true);
      expect(mockGoto).not.toHaveBeenCalled();
    });

    it('should redirect to unauthorized when user cannot perform TARA', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canPerformTARA.mockReturnValue(false);

      expect(requireTARAAccess()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
    });
  });

  describe('Integration Tests', () => {
    it('should handle authentication check before permission check', () => {
      // First call - unauthenticated
      mockGet.mockReturnValue({
        isAuthenticated: false,
        user: null
      });

      expect(requireUserManagement()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/login');
      expect(mockPermissions.canViewUserManagement).not.toHaveBeenCalled();
    });

    it('should check permissions only after authentication passes', () => {
      mockGet.mockReturnValue({
        isAuthenticated: true,
        user: { user_id: '123' }
      });
      mockPermissions.canViewUserManagement.mockReturnValue(false);

      expect(requireUserManagement()).toBe(false);
      expect(mockGoto).toHaveBeenCalledWith('/unauthorized');
      expect(mockPermissions.canViewUserManagement).toHaveBeenCalled();
    });
  });
});
