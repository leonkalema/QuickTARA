import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, fireEvent, waitFor, screen } from '@testing-library/svelte';
import UserTable from './UserTable.svelte';
import { UserRole, OrgRole } from '$lib/types/roles';

// Mock dependencies
vi.mock('$lib/api/userApi', () => ({
  userApi: {
    createUser: vi.fn(),
    updateUser: vi.fn(),
    deleteUser: vi.fn()
  }
}));

vi.mock('$lib/stores/notifications', () => ({
  notifications: {
    show: vi.fn()
  }
}));

vi.mock('$lib/stores/auth', () => ({
  authStore: {
    subscribe: vi.fn(),
  }
}));

vi.mock('svelte/store', () => ({
  get: vi.fn(() => ({
    token: 'mock-token'
  }))
}));

vi.mock('$lib/config', () => ({
  API_BASE_URL: 'http://localhost:8000'
}));

vi.mock('$lib/utils/permissions', () => ({
  canCreateUsers: vi.fn(() => true),
  canEditUsers: vi.fn(() => true),
  canDeleteUsers: vi.fn(() => true)
}));

// Mock fetch
global.fetch = vi.fn();

describe('UserTable - Organization Assignment', () => {
  const mockUsers = [
    {
      user_id: '1',
      email: 'user1@example.com',
      username: 'user1',
      first_name: 'User',
      last_name: 'One',
      status: 'active',
      created_at: '2024-01-01T00:00:00Z'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock organizations API response
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([
        { organization_id: 'org1', name: 'Test Organization 1' },
        { organization_id: 'org2', name: 'Test Organization 2' }
      ])
    });
  });

  describe('Add User Form', () => {
    it('should show organization assignment section when adding new user', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        expect(screen.getByLabelText(/Organization \*/)).toBeInTheDocument();
        expect(screen.getByLabelText(/Organization Role \*/)).toBeInTheDocument();
      });
    });

    it('should load organizations on mount', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/organizations',
          expect.objectContaining({
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-token'
            })
          })
        );
      });
    });

    it('should populate organization dropdown with loaded data', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        const orgSelect = screen.getByLabelText(/Organization \*/);
        expect(orgSelect).toContainHTML('Test Organization 1');
        expect(orgSelect).toContainHTML('Test Organization 2');
      });
    });

    it('should show organization roles with proper labels', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        const roleSelect = screen.getByLabelText(/Organization Role \*/);
        expect(roleSelect).toContainHTML('Tool Admin');
        expect(roleSelect).toContainHTML('Organization Admin');
        expect(roleSelect).toContainHTML('Analyst');
        expect(roleSelect).toContainHTML('Viewer');
      });
    });

    it('should mark organization fields as required', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        const orgSelect = screen.getByLabelText(/Organization \*/);
        const roleSelect = screen.getByLabelText(/Organization Role \*/);
        
        expect(orgSelect).toHaveAttribute('required');
        expect(roleSelect).toHaveAttribute('required');
      });
    });
  });

  describe('Validation', () => {
    it('should validate organization selection before submission', async () => {
      const { notifications } = await import('$lib/stores/notifications');
      
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      // Fill required fields but leave organization empty
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Email address/)).toBeInTheDocument();
      });
      
      await fireEvent.input(screen.getByPlaceholderText(/Email address/), { 
        target: { value: 'test@example.com' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Username/), { 
        target: { value: 'testuser' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/First Name/), { 
        target: { value: 'Test' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Last Name/), { 
        target: { value: 'User' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Password/), { 
        target: { value: 'password123' } 
      });
      
      // Leave organization empty and try to submit
      const submitButton = screen.getByText('Add User');
      await fireEvent.click(submitButton);
      
      expect(notifications.show).toHaveBeenCalledWith(
        'Please select an organization', 
        'error'
      );
    });

    it('should validate organization role selection before submission', async () => {
      const { notifications } = await import('$lib/stores/notifications');
      
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      // Fill required fields and organization but leave role empty
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Email address/)).toBeInTheDocument();
      });
      
      await fireEvent.input(screen.getByPlaceholderText(/Email address/), { 
        target: { value: 'test@example.com' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Username/), { 
        target: { value: 'testuser' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/First Name/), { 
        target: { value: 'Test' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Last Name/), { 
        target: { value: 'User' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Password/), { 
        target: { value: 'password123' } 
      });
      
      // Set organization but leave role empty
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { 
        target: { value: 'org1' } 
      });
      
      const submitButton = screen.getByText('Add User');
      await fireEvent.click(submitButton);
      
      expect(notifications.show).toHaveBeenCalledWith(
        'Please select an organization role', 
        'error'
      );
    });

    it('should allow submission when all required fields including org assignment are filled', async () => {
      const mockCreateUser = vi.fn().mockResolvedValue({ user_id: 'new-user-123' });
      const { userApi } = await import('$lib/api/userApi');
      (userApi.createUser as any) = mockCreateUser;
      
      // Mock organization assignment API call
      (global.fetch as any).mockImplementation((url: string, options: any) => {
        if (url.includes('/organizations') && !options?.method) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([
              { organization_id: 'org1', name: 'Test Organization 1' }
            ])
          });
        }
        if (url.includes('/members') && options?.method === 'POST') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      // Fill all required fields
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Email address/)).toBeInTheDocument();
      });
      
      await fireEvent.input(screen.getByPlaceholderText(/Email address/), { 
        target: { value: 'test@example.com' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Username/), { 
        target: { value: 'testuser' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/First Name/), { 
        target: { value: 'Test' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Last Name/), { 
        target: { value: 'User' } 
      });
      await fireEvent.input(screen.getByPlaceholderText(/Password/), { 
        target: { value: 'password123' } 
      });
      
      // Set organization and role
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { 
        target: { value: 'org1' } 
      });
      await fireEvent.change(screen.getByLabelText(/Organization Role \*/), { 
        target: { value: OrgRole.ANALYST } 
      });
      
      const submitButton = screen.getByText('Add User');
      await fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockCreateUser).toHaveBeenCalledWith({
          email: 'test@example.com',
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User',
          password: 'password123',
          role: UserRole.ANALYST,
          status: 'active'
        });
      });
    });
  });

  describe('Form Reset', () => {
    it('should reset organization fields when form is reset', async () => {
      render(UserTable, { 
        users: mockUsers, 
        isAddingNew: true 
      });
      
      await waitFor(() => {
        expect(screen.getByLabelText(/Organization \*/)).toBeInTheDocument();
      });
      
      // Set values
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { 
        target: { value: 'org1' } 
      });
      await fireEvent.change(screen.getByLabelText(/Organization Role \*/), { 
        target: { value: OrgRole.ORG_ADMIN } 
      });
      
      // Cancel/reset form
      const cancelButton = screen.getByText('Cancel');
      await fireEvent.click(cancelButton);
      
      // Form should be reset (component will re-render with isAddingNew: false)
      expect(screen.queryByLabelText(/Organization \*/)).not.toBeInTheDocument();
    });
  });

  describe('Default Values', () => {
    it('should set default organization and role when organizations load', async () => {
      render(UserTable, {
        users: mockUsers,
        isAddingNew: true
      });

      await waitFor(() => {
        const orgSelect = screen.getByLabelText(/Organization \*/) as HTMLSelectElement;
        const roleSelect = screen.getByLabelText(/Organization Role \*/) as HTMLSelectElement;

        // Should default to first organization and ANALYST role
        expect(orgSelect.value).toBe('org1');
        expect(roleSelect.value).toBe(OrgRole.ANALYST);
      });
    });
  });
});

// ---------------------------------------------------------------------------
// Role column display tests (the bug fix)
// ---------------------------------------------------------------------------
describe('UserTable - Role Column Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ organizations: [] })
    });
  });

  it('shows "Tool Admin" badge for superusers', async () => {
    const users = [
      {
        user_id: 'admin-1',
        email: 'admin@example.com',
        username: 'admin',
        first_name: 'Admin',
        last_name: 'User',
        role: 'tool_admin',
        status: 'active',
        is_superuser: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: []
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      expect(screen.getByText('Tool Admin')).toBeInTheDocument();
    });
  });

  it('shows the org role label for a regular user with an org assignment', async () => {
    const users = [
      {
        user_id: 'analyst-1',
        email: 'analyst@example.com',
        username: 'analyst',
        first_name: 'Jane',
        last_name: 'Doe',
        role: 'analyst',
        status: 'active',
        is_superuser: false,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: [{ organization_id: 'org-1', role: 'analyst' }]
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      expect(screen.getByText('Analyst')).toBeInTheDocument();
    });
    // Should NOT show the old hardcoded "User" text
    expect(screen.queryByText('User')).not.toBeInTheDocument();
  });

  it('shows "Risk Manager" label for a risk_manager role', async () => {
    const users = [
      {
        user_id: 'rm-1',
        email: 'rm@example.com',
        username: 'rm',
        first_name: 'Risk',
        last_name: 'Manager',
        role: 'risk_manager',
        status: 'active',
        is_superuser: false,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: [{ organization_id: 'org-1', role: 'risk_manager' }]
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      expect(screen.getByText('Risk Manager')).toBeInTheDocument();
    });
  });

  it('shows "No Role" for a user with no org assignments', async () => {
    const users = [
      {
        user_id: 'norole-1',
        email: 'norole@example.com',
        username: 'norole',
        first_name: 'No',
        last_name: 'Role',
        role: 'analyst',
        status: 'active',
        is_superuser: false,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: []
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      expect(screen.getByText('No Role')).toBeInTheDocument();
    });
    // Should NOT show the old hardcoded "User" text
    expect(screen.queryByText('User')).not.toBeInTheDocument();
  });

  it('shows role from first org when user belongs to multiple orgs', async () => {
    const users = [
      {
        user_id: 'multi-1',
        email: 'multi@example.com',
        username: 'multi',
        first_name: 'Multi',
        last_name: 'Org',
        role: 'viewer',
        status: 'active',
        is_superuser: false,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: [
          { organization_id: 'org-1', role: 'viewer' },
          { organization_id: 'org-2', role: 'analyst' }
        ]
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      // First org role (viewer) displayed
      expect(screen.getByText('Viewer')).toBeInTheDocument();
    });
  });

  it('does not show "User" (old hardcoded value) for any user', async () => {
    const users = [
      {
        user_id: 'u1',
        email: 'u1@example.com',
        username: 'u1',
        first_name: 'A',
        last_name: 'B',
        role: 'auditor',
        status: 'active',
        is_superuser: false,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        organizations: [{ organization_id: 'org-1', role: 'auditor' }]
      }
    ];

    render(UserTable, { users, isAddingNew: false });

    await waitFor(() => {
      expect(screen.getByText('Auditor')).toBeInTheDocument();
    });
    // The old bug: role column showed the literal string "User"
    expect(screen.queryByText('User')).not.toBeInTheDocument();
  });
});
