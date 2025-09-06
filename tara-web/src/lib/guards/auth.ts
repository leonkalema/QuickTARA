import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

export interface RouteGuardOptions {
	requireAuth?: boolean;
	requiredRoles?: string[];
	requiredPermissions?: string[];
	redirectTo?: string;
}

export async function authGuard(options: RouteGuardOptions = {}) {
	const {
		requireAuth = true,
		requiredRoles = [],
		requiredPermissions = [],
		redirectTo = '/auth'
	} = options;

	const auth = get(authStore);

	// Check authentication
	if (requireAuth && !auth.isAuthenticated) {
		throw redirect(302, redirectTo);
	}

	// Check token validity and refresh if needed
	if (auth.isAuthenticated) {
		const tokenValid = await authStore.checkAndRefreshToken();
		if (!tokenValid) {
			throw redirect(302, redirectTo);
		}
	}

	// Check roles
	if (requiredRoles.length > 0) {
		const hasRequiredRole = requiredRoles.some(role => {
			const userRole = auth.user?.organizations?.[0]?.role;
			return userRole === role;
		});
		if (!hasRequiredRole) {
			throw redirect(302, '/unauthorized');
		}
	}

	// Check permissions
	if (requiredPermissions.length > 0) {
		// For now, assume Tool Admin has all permissions
		const userRole = auth.user?.organizations?.[0]?.role;
		const hasRequiredPermission = userRole === 'Tool Admin';
		if (!hasRequiredPermission) {
			throw redirect(302, '/unauthorized');
		}
	}

	return true;
}

// Predefined guard functions for common use cases
export const requireAuth = () => authGuard({ requireAuth: true });

export const requireAdmin = () => authGuard({ 
	requireAuth: true, 
	requiredRoles: ['Tool Admin'] 
});

export const requireOrgAdmin = () => authGuard({ 
	requireAuth: true, 
	requiredRoles: ['Tool Admin', 'Org Admin'] 
});

export const requireRiskManager = () => authGuard({ 
	requireAuth: true, 
	requiredRoles: ['Tool Admin', 'Org Admin', 'Risk Manager'] 
});

export const requireAnalyst = () => authGuard({ 
	requireAuth: true, 
	requiredRoles: ['Tool Admin', 'Org Admin', 'Risk Manager', 'TARA Analyst', 'Security Engineer'] 
});

// Permission-based guards
export const requireCreatePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['create_threat', 'create_damage_scenario', 'create_asset']
});

export const requireReadPermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['read_threat', 'read_damage_scenario', 'read_asset']
});

export const requireUpdatePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['update_threat', 'update_damage_scenario', 'update_asset']
});

export const requireDeletePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['delete_threat', 'delete_damage_scenario', 'delete_asset']
});
