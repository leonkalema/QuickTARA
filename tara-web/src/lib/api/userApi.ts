import { authStore } from '$lib/stores/auth';
import { get } from 'svelte/store';
import { API_BASE_URL } from '$lib/config';

export interface User {
  user_id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  status: string;
  is_verified: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface CreateUserRequest {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  role: string;
  status: string;
}

export interface UpdateUserRequest {
  email?: string;
  full_name?: string;
  is_active?: boolean;
  role?: string;
}

class UserApiService {
  private getAuthHeaders() {
    const auth = get(authStore);
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${auth.token}`
    };
  }

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.statusText}`);
    }

    return response.json();
  }

  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Create user error:', error);
      throw new Error(error.detail || JSON.stringify(error) || 'Failed to create user');
    }

    return response.json();
  }

  async updateUser(userId: string, updates: UpdateUserRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update user');
    }

    return response.json();
  }

  async deleteUser(userId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete user');
    }
  }

  async toggleUserStatus(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/toggle-status`, {
      method: 'PATCH',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to toggle user status');
    }

    return response.json();
  }
}

export const userApi = new UserApiService();
