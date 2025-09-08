import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '$lib/api/auth';

// Utility function to decode JWT and get expiry
function getTokenExpiry(token: string): number | null {
	try {
		const payload = JSON.parse(atob(token.split('.')[1]));
		return payload.exp ? payload.exp * 1000 : null; // Convert to milliseconds
	} catch (error) {
		console.error('Error decoding token:', error);
		return null;
	}
}

// Check if token is expired or will expire soon (within 5 minutes)
function isTokenExpired(expiry: number | null): boolean {
	if (!expiry) return true;
	const now = Date.now();
	const fiveMinutes = 5 * 60 * 1000;
	return expiry - now < fiveMinutes;
}

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
	organizations: Array<{
		organization_id: string;
		name: string;
		role: string;
		permissions: string[];
	}>;
}

export interface AuthState {
	user: User | null;
	token: string | null;
	refreshToken: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	tokenExpiry: number | null;
}

const initialState: AuthState = {
	user: null,
	token: null,
	refreshToken: null,
	isAuthenticated: false,
	isLoading: false,
	tokenExpiry: null
};

// Create the auth store
function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,
		
		// Set loading state
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, isLoading: loading }));
		},

		// Login success
		login: (user: User, token: string, refreshToken: string) => {
			// Decode token to get expiry time
			const tokenExpiry = getTokenExpiry(token);
			
			const newState: AuthState = {
				user,
				token,
				refreshToken,
				isAuthenticated: true,
				isLoading: false,
				tokenExpiry
			};
			
			set(newState);
			
			// Store tokens in localStorage if in browser
			if (browser) {
				localStorage.setItem('auth_token', token);
				localStorage.setItem('refresh_token', refreshToken);
				localStorage.setItem('user', JSON.stringify(user));
			}
		},

		// Logout
		logout: () => {
			set(initialState);
			
			// Clear localStorage if in browser
			if (browser) {
				localStorage.removeItem('auth_token');
				localStorage.removeItem('refresh_token');
				localStorage.removeItem('user');
			}
		},

		// Update user info
		updateUser: (user: User) => {
			update(state => ({ ...state, user }));
			
			if (browser) {
				localStorage.setItem('user', JSON.stringify(user));
			}
		},

		// Initialize from localStorage
		init: () => {
			if (!browser) return;
			
			const token = localStorage.getItem('auth_token');
			const refreshToken = localStorage.getItem('refresh_token');
			const userStr = localStorage.getItem('user');
			
			if (token && refreshToken && userStr) {
				try {
					const user = JSON.parse(userStr);
					const tokenExpiry = getTokenExpiry(token);
					set({
						user,
						token,
						refreshToken,
						isAuthenticated: true,
						isLoading: false,
						tokenExpiry
					});
				} catch (error) {
					console.error('Error parsing stored user data:', error);
					// Clear invalid data
					localStorage.removeItem('auth_token');
					localStorage.removeItem('refresh_token');
					localStorage.removeItem('user');
				}
			}
		},

		// Update token (for refresh)
		updateToken: (newToken: string) => {
			const tokenExpiry = getTokenExpiry(newToken);
			update(state => ({ ...state, token: newToken, tokenExpiry }));
			
			if (browser) {
				localStorage.setItem('auth_token', newToken);
			}
		},

		// Check if token needs refresh and refresh if needed
		checkAndRefreshToken: async () => {
			const state = get(authStore);
			
			if (!state.isAuthenticated || !state.refreshToken || !state.tokenExpiry) {
				return false;
			}

			if (isTokenExpired(state.tokenExpiry)) {
				try {
					const response = await authApi.refreshToken(state.refreshToken);
					authStore.updateToken(response.access_token);
					return true;
				} catch (error) {
					console.error('Token refresh failed:', error);
					authStore.logout();
					return false;
				}
			}
			
			return true;
		},

		// Get user permissions
		getUserPermissions: (): string[] => {
			const state = get(authStore);
			if (!state.user?.organizations) return [];
			
			return state.user.organizations.reduce((permissions: string[], org: any) => {
				return [...permissions, ...org.permissions];
			}, []);
		},

		// Check if user has specific permission
		hasPermission: (permission: string): boolean => {
			const permissions = authStore.getUserPermissions();
			return permissions.includes(permission);
		},

		// Check if user has specific role
		hasRole: (role: string): boolean => {
			const state = get(authStore);
			if (!state.user?.organizations) return false;
			
			return state.user.organizations.some((org: any) => org.role === role);
		}
	};
}

export const authStore = createAuthStore();

// Initialize auth store when module loads (but don't auto-redirect)
if (browser) {
	// Use setTimeout to avoid immediate redirects during SSR/hydration
	setTimeout(() => {
		authStore.init();
	}, 100);
}
