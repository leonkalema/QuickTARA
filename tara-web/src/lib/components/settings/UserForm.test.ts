import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, fireEvent, waitFor, screen } from '@testing-library/svelte';
import UserForm from './UserForm.svelte';
import { UserRole, OrgRole } from '$lib/types/roles';

// Mock dependencies
vi.mock('$lib/api/userApi', () => ({
  userApi: {
    createUser: vi.fn(),
    updateUser: vi.fn()
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
    // Mock store will be set up in tests
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

// Mock fetch
global.fetch = vi.fn();

describe('UserForm - Organization Assignment', () => {
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

  describe('New User Creation', () => {
    it('should show organization assignment fields for new users', async () => {
      render(UserForm, { user: null });
      
      await waitFor(() => {
        expect(screen.getByLabelText(/Organization \*/)).toBeInTheDocument();
        expect(screen.getByLabelText(/Organization Role \*/)).toBeInTheDocument();
      });
    });

    it('should load organizations on mount', async () => {
      render(UserForm, { user: null });
      
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
      render(UserForm, { user: null });
      
      await waitFor(() => {
        const orgSelect = screen.getByLabelText(/Organization \*/);
        expect(orgSelect).toContainHTML('Test Organization 1');
        expect(orgSelect).toContainHTML('Test Organization 2');
      });
    });

    it('should populate organization role dropdown with enum values', async () => {
      render(UserForm, { user: null });
      
      await waitFor(() => {
        const roleSelect = screen.getByLabelText(/Organization Role \*/);
        expect(roleSelect).toContainHTML('Tool Admin');
        expect(roleSelect).toContainHTML('Organization Admin');
        expect(roleSelect).toContainHTML('TARA Analyst');
        expect(roleSelect).toContainHTML('Viewer');
      });
    });

    it('should set default values when organizations are loaded', async () => {
      render(UserForm, { user: null });
      
      await waitFor(() => {
        const orgSelect = screen.getByLabelText(/Organization \*/) as HTMLSelectElement;
        const roleSelect = screen.getByLabelText(/Organization Role \*/) as HTMLSelectElement;
        
        expect(orgSelect.value).toBe('org1'); // First organization
        expect(roleSelect.value).toBe(OrgRole.TARA_ANALYST);
      });
    });
  });

  describe('Validation', () => {
    it('should validate organization selection for new users', async () => {
      const { component } = render(UserForm, { user: null });
      
      // Fill required fields but leave organization empty
      await fireEvent.input(screen.getByLabelText(/Email/), { target: { value: 'test@example.com' } });
      await fireEvent.input(screen.getByLabelText(/Username/), { target: { value: 'testuser' } });
      await fireEvent.input(screen.getByLabelText(/First Name/), { target: { value: 'Test' } });
      await fireEvent.input(screen.getByLabelText(/Last Name/), { target: { value: 'User' } });
      await fireEvent.input(screen.getByLabelText(/Password/), { target: { value: 'password123' } });
      
      // Clear organization selection
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { target: { value: '' } });
      
      // Try to submit
      const form = screen.getByRole('form') || screen.getByTestId('user-form');
      await fireEvent.submit(form);
      
      await waitFor(() => {
        expect(screen.getByText('Organization is required')).toBeInTheDocument();
      });
    });

    it('should validate organization role selection for new users', async () => {
      const { component } = render(UserForm, { user: null });
      
      // Fill required fields but leave organization role empty
      await fireEvent.input(screen.getByLabelText(/Email/), { target: { value: 'test@example.com' } });
      await fireEvent.input(screen.getByLabelText(/Username/), { target: { value: 'testuser' } });
      await fireEvent.input(screen.getByLabelText(/First Name/), { target: { value: 'Test' } });
      await fireEvent.input(screen.getByLabelText(/Last Name/), { target: { value: 'User' } });
      await fireEvent.input(screen.getByLabelText(/Password/), { target: { value: 'password123' } });
      
      // Set organization but clear role
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { target: { value: 'org1' } });
      await fireEvent.change(screen.getByLabelText(/Organization Role \*/), { target: { value: '' } });
      
      // Try to submit
      const form = screen.getByRole('form') || screen.getByTestId('user-form');
      await fireEvent.submit(form);
      
      await waitFor(() => {
        expect(screen.getByText('Organization role is required')).toBeInTheDocument();
      });
    });

    it('should not show organization fields for existing users', async () => {
      const existingUser = {
        user_id: '123',
        email: 'existing@example.com',
        username: 'existing',
        first_name: 'Existing',
        last_name: 'User',
        status: 'active'
      };
      
      render(UserForm, { user: existingUser });
      
      // Organization fields should not be present for existing users
      expect(screen.queryByLabelText(/Organization \*/)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Organization Role \*/)).not.toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should include organization assignment in user creation', async () => {
      const mockCreateUser = vi.fn().mockResolvedValue({ user_id: 'new-user-123' });
      const mockAssignToOrg = vi.fn().mockResolvedValue({});
      
      // Mock the userApi
      const { userApi } = await import('$lib/api/userApi');
      (userApi.createUser as any) = mockCreateUser;
      
      // Mock organization assignment API call
      (global.fetch as any).mockImplementation((url: string, options: any) => {
        if (url.includes('/organizations')) {
          if (options?.method === 'POST') {
            return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
          }
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([
              { organization_id: 'org1', name: 'Test Organization 1' }
            ])
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      
      render(UserForm, { user: null });
      
      // Wait for organizations to load and fill form
      await waitFor(() => {
        expect(screen.getByLabelText(/Organization \*/)).toBeInTheDocument();
      });
      
      await fireEvent.input(screen.getByLabelText(/Email/), { target: { value: 'test@example.com' } });
      await fireEvent.input(screen.getByLabelText(/Username/), { target: { value: 'testuser' } });
      await fireEvent.input(screen.getByLabelText(/First Name/), { target: { value: 'Test' } });
      await fireEvent.input(screen.getByLabelText(/Last Name/), { target: { value: 'User' } });
      await fireEvent.input(screen.getByLabelText(/Password/), { target: { value: 'password123' } });
      await fireEvent.input(screen.getByLabelText(/Confirm Password/), { target: { value: 'password123' } });
      
      // Set organization and role
      await fireEvent.change(screen.getByLabelText(/Organization \*/), { target: { value: 'org1' } });
      await fireEvent.change(screen.getByLabelText(/Organization Role \*/), { target: { value: OrgRole.TARA_ANALYST } });
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: /Create User/ });
      await fireEvent.click(submitButton);
      
      await waitFor(() => {
        // Verify user creation was called
        expect(mockCreateUser).toHaveBeenCalledWith({
          email: 'test@example.com',
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User',
          password: 'password123',
          role: UserRole.TARA_ANALYST,
          status: 'active'
        });
        
        // Verify organization assignment API was called
        expect(global.fetch).toHaveBeenCalledWith(
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
    });
  });

  describe('Error Handling', () => {
    it('should handle organization loading failure gracefully', async () => {
      (global.fetch as any).mockRejectedValue(new Error('Network error'));
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      render(UserForm, { user: null });
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to load organizations:', expect.any(Error));
      });
      
      consoleSpy.mockRestore();
    });
  });
});
