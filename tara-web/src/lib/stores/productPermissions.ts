import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { authStore } from './auth';
import { API_BASE_URL } from '$lib/config';

export interface ProductPermissions {
	scope_id: string;
	organization_id: string | null;
	can_view: boolean;
	can_edit: boolean;
	can_delete: boolean;
	can_manage_assets: boolean;
	can_manage_scenarios: boolean;
	can_approve_risks: boolean;
	role: string | null;
}

interface PermissionsState {
	permissions: Record<string, ProductPermissions>;
	loading: boolean;
	currentProductId: string | null;
}

const initialState: PermissionsState = {
	permissions: {},
	loading: false,
	currentProductId: null
};

function createProductPermissionsStore() {
	const { subscribe, set, update } = writable<PermissionsState>(initialState);

	return {
		subscribe,

		async fetchPermissions(scopeId: string): Promise<ProductPermissions | null> {
			if (!browser) return null;

			const auth = get(authStore);
			const tokenFromStorage = localStorage.getItem('auth_token');
			const token = auth.token ?? tokenFromStorage;
			if (!token) return null;

			update(state => ({ ...state, loading: true }));

			try {
				const response = await fetch(`${API_BASE_URL}/products/${scopeId}/permissions`, {
					headers: {
						'Authorization': `Bearer ${token}`,
						'Content-Type': 'application/json'
					}
				});

				if (response.ok) {
					const permissions: ProductPermissions = await response.json();
					update(state => ({
						...state,
						permissions: { ...state.permissions, [scopeId]: permissions },
						loading: false,
						currentProductId: scopeId
					}));
					return permissions;
				}
				update(state => ({ ...state, loading: false }));
				return null;
			} catch (error) {
				console.error('Failed to fetch product permissions:', error);
				update(state => ({ ...state, loading: false }));
				return null;
			}
		},

		getPermissions(scopeId: string): ProductPermissions | null {
			const state = get({ subscribe });
			return state.permissions[scopeId] || null;
		},

		getCurrentPermissions(): ProductPermissions | null {
			const state = get({ subscribe });
			if (!state.currentProductId) return null;
			return state.permissions[state.currentProductId] || null;
		},

		setCurrentProduct(scopeId: string | null) {
			update(state => ({ ...state, currentProductId: scopeId }));
		},

		canView(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_view ?? false;
		},

		canEdit(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_edit ?? false;
		},

		canDelete(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_delete ?? false;
		},

		canManageAssets(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_manage_assets ?? false;
		},

		canManageScenarios(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_manage_scenarios ?? false;
		},

		canApproveRisks(scopeId?: string): boolean {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return false;
			const perms = state.permissions[id];
			return perms?.can_approve_risks ?? false;
		},

		getRole(scopeId?: string): string | null {
			const state = get({ subscribe });
			const id = scopeId || state.currentProductId;
			if (!id) return null;
			const perms = state.permissions[id];
			return perms?.role ?? null;
		},

		clearPermissions() {
			set(initialState);
		}
	};
}

export const productPermissions = createProductPermissionsStore();
