import { API_BASE_URL } from '$lib/config';

export interface LoginRequest {
	email: string;
	password: string;
}

export interface RegisterRequest {
	email: string;
	username: string;
	first_name: string;
	last_name: string;
	password: string;
	organization_id?: string;
}

export interface LoginResponse {
	access_token: string;
	refresh_token: string;
	token_type: string;
	expires_in: number;
}

export interface UserResponse {
	user_id: string;
	email: string;
	username: string;
	first_name: string;
	last_name: string;
	status: string;
	is_verified: boolean;
	created_at: string;
	organizations: any[];
}

export interface RefreshRequest {
	refresh_token: string;
}

class AuthApiError extends Error {
	constructor(public status: number, message: string, public details?: any) {
		super(message);
		this.name = 'AuthApiError';
	}
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new AuthApiError(
			response.status,
			errorData.detail || `HTTP ${response.status}`,
			errorData
		);
	}
	return response.json();
}

export const authApi = {
	async login(credentials: LoginRequest): Promise<LoginResponse> {
		const response = await fetch(`${API_BASE_URL}/auth/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(credentials),
		});
		
		return handleResponse<LoginResponse>(response);
	},

	async register(userData: RegisterRequest): Promise<UserResponse> {
		const response = await fetch(`${API_BASE_URL}/auth/register`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(userData),
		});
		
		return handleResponse<UserResponse>(response);
	},

	async getCurrentUser(token: string): Promise<UserResponse> {
		const response = await fetch(`${API_BASE_URL}/auth/me`, {
			method: 'GET',
			headers: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json',
			},
		});
		
		return handleResponse<UserResponse>(response);
	},

	async refreshToken(refreshToken: string): Promise<LoginResponse> {
		const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ refresh_token: refreshToken }),
		});
		
		return handleResponse<LoginResponse>(response);
	},

	async logout(refreshToken: string): Promise<void> {
		const response = await fetch(`${API_BASE_URL}/auth/logout`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ refresh_token: refreshToken }),
		});
		
		if (!response.ok) {
			// Don't throw error for logout - just log it
			console.warn('Logout request failed:', response.status);
		}
	}
};

export { AuthApiError };
