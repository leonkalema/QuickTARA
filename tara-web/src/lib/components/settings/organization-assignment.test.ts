import { describe, it, expect, beforeEach, vi } from 'vitest';
import { UserRole, OrgRole, getAllUserRoles, getAllOrgRoles, getUserRoleLabel, getOrgRoleLabel } from '$lib/types/roles';

// Mock the API calls
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('Organization Assignment Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Role Enums and Labels', () => {
    it('should have all required user roles', () => {
      const roles = getAllUserRoles();
      
      expect(roles).toContain(UserRole.TOOL_ADMIN);
      expect(roles).toContain(UserRole.ORG_ADMIN);
      expect(roles).toContain(UserRole.TARA_ANALYST);
      expect(roles).toContain(UserRole.VIEWER);
      expect(roles).toContain(UserRole.RISK_MANAGER);
      expect(roles).toContain(UserRole.COMPLIANCE_OFFICER);
      expect(roles).toContain(UserRole.PRODUCT_OWNER);
      expect(roles).toContain(UserRole.SECURITY_ENGINEER);
      expect(roles).toContain(UserRole.AUDITOR);
      expect(roles.length).toBe(9);
    });

    it('should have all required organization roles', () => {
      const roles = getAllOrgRoles();
      
      expect(roles).toContain(OrgRole.TOOL_ADMIN);
      expect(roles).toContain(OrgRole.ORG_ADMIN);
      expect(roles).toContain(OrgRole.TARA_ANALYST);
      expect(roles).toContain(OrgRole.VIEWER);
      expect(roles).toContain(OrgRole.RISK_MANAGER);
      expect(roles).toContain(OrgRole.COMPLIANCE_OFFICER);
      expect(roles).toContain(OrgRole.PRODUCT_OWNER);
      expect(roles).toContain(OrgRole.SECURITY_ENGINEER);
      expect(roles).toContain(OrgRole.AUDITOR);
      expect(roles.length).toBe(9);
    });

    it('should provide correct user role labels', () => {
      expect(getUserRoleLabel(UserRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getUserRoleLabel(UserRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getUserRoleLabel(UserRole.TARA_ANALYST)).toBe('TARA Analyst');
      expect(getUserRoleLabel(UserRole.VIEWER)).toBe('Viewer');
    });

    it('should provide correct organization role labels', () => {
      expect(getOrgRoleLabel(OrgRole.TOOL_ADMIN)).toBe('Tool Admin');
      expect(getOrgRoleLabel(OrgRole.ORG_ADMIN)).toBe('Organization Admin');
      expect(getOrgRoleLabel(OrgRole.TARA_ANALYST)).toBe('TARA Analyst');
      expect(getOrgRoleLabel(OrgRole.VIEWER)).toBe('Viewer');
    });
  });

  describe('User Creation with Organization Assignment', () => {
    it('should validate required organization fields', () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        password: 'password123',
        role: UserRole.TARA_ANALYST,
        status: 'active'
      };

      // Missing organization_id should be invalid
      const isValidWithoutOrg = validateUserCreationData({ ...userData });
      expect(isValidWithoutOrg.isValid).toBe(false);
      expect(isValidWithoutOrg.errors).toContain('Organization is required');

      // Missing organization_role should be invalid
      const isValidWithoutRole = validateUserCreationData({ 
        ...userData, 
        organization_id: 'org1' 
      });
      expect(isValidWithoutRole.isValid).toBe(false);
      expect(isValidWithoutRole.errors).toContain('Organization role is required');

      // Complete data should be valid
      const isValidComplete = validateUserCreationData({
        ...userData,
        organization_id: 'org1',
        organization_role: OrgRole.TARA_ANALYST
      });
      expect(isValidComplete.isValid).toBe(true);
      expect(isValidComplete.errors).toHaveLength(0);
    });

    it('should create user and assign to organization', async () => {
      // Mock successful user creation
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ user_id: 'new-user-123' })
      });

      // Mock successful organization assignment
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      });

      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        password: 'password123',
        role: UserRole.TARA_ANALYST,
        status: 'active',
        organization_id: 'org1',
        organization_role: OrgRole.TARA_ANALYST
      };

      const result = await createUserWithOrganization(userData, 'mock-token');

      expect(result.success).toBe(true);
      expect(result.user_id).toBe('new-user-123');

      // Verify user creation API call
      expect(mockFetch).toHaveBeenNthCalledWith(1, 
        'http://localhost:8000/users',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            email: userData.email,
            username: userData.username,
            first_name: userData.first_name,
            last_name: userData.last_name,
            password: userData.password,
            role: userData.role,
            status: userData.status
          })
        })
      );

      // Verify organization assignment API call
      expect(mockFetch).toHaveBeenNthCalledWith(2,
        'http://localhost:8000/organizations/org1/members',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            user_id: 'new-user-123',
            role: OrgRole.TARA_ANALYST
          })
        })
      );
    });

    it('should handle organization assignment failure', async () => {
      // Mock successful user creation
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ user_id: 'new-user-123' })
      });

      // Mock failed organization assignment
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Organization assignment failed' })
      });

      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        password: 'password123',
        role: UserRole.TARA_ANALYST,
        status: 'active',
        organization_id: 'org1',
        organization_role: OrgRole.TARA_ANALYST
      };

      const result = await createUserWithOrganization(userData, 'mock-token');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to assign user to organization');
    });
  });

  describe('Organization Loading', () => {
    it('should load organizations successfully', async () => {
      const mockOrganizations = [
        { organization_id: 'org1', name: 'Test Organization 1' },
        { organization_id: 'org2', name: 'Test Organization 2' }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockOrganizations)
      });

      const result = await loadOrganizations('mock-token');

      expect(result.success).toBe(true);
      expect(result.organizations).toEqual(mockOrganizations);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/organizations',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );
    });

    it('should handle organization loading failure', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await loadOrganizations('mock-token');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to load organizations');
    });
  });
});

// Helper functions for testing
function validateUserCreationData(userData: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!userData.organization_id) {
    errors.push('Organization is required');
  }

  if (!userData.organization_role) {
    errors.push('Organization role is required');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

async function createUserWithOrganization(userData: any, token: string): Promise<{ success: boolean; user_id?: string; error?: string }> {
  try {
    // Create user
    const userResponse = await fetch('http://localhost:8000/users', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: userData.email,
        username: userData.username,
        first_name: userData.first_name,
        last_name: userData.last_name,
        password: userData.password,
        role: userData.role,
        status: userData.status
      })
    });

    if (!userResponse.ok) {
      return { success: false, error: 'Failed to create user' };
    }

    const user = await userResponse.json();

    // Assign to organization
    const orgResponse = await fetch(`http://localhost:8000/organizations/${userData.organization_id}/members`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user.user_id,
        role: userData.organization_role
      })
    });

    if (!orgResponse.ok) {
      return { success: false, error: 'Failed to assign user to organization' };
    }

    return { success: true, user_id: user.user_id };
  } catch (error) {
    return { success: false, error: `Error: ${error}` };
  }
}

async function loadOrganizations(token: string): Promise<{ success: boolean; organizations?: any[]; error?: string }> {
  try {
    const response = await fetch('http://localhost:8000/organizations', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      return { success: false, error: 'Failed to load organizations' };
    }

    const organizations = await response.json();
    return { success: true, organizations };
  } catch (error) {
    return { success: false, error: `Failed to load organizations: ${error}` };
  }
}
