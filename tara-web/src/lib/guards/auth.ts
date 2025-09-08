import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

export interface RouteGuardOptions {
    requireAuth?: boolean;
    requiredRoles?: string[];
    requiredPermissions?: string[];
    redirectTo?: string;
}

// Backend role values (snake_case)
export const Role = {
    TOOL_ADMIN: 'tool_admin',
    ORG_ADMIN: 'org_admin',
    RISK_MANAGER: 'risk_manager',
    TARA_ANALYST: 'tara_analyst',
    SECURITY_ENGINEER: 'security_engineer',
    COMPLIANCE_OFFICER: 'compliance_officer',
    PRODUCT_OWNER: 'product_owner',
    AUDITOR: 'auditor',
    VIEWER: 'viewer'
} as const;

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

	    // Helper: determine superuser, prefer user payload, fallback to token decode
    const isSuperuser = (() => {
        const userFlag = (auth.user as any)?.is_superuser === true;
        if (userFlag) return true;
        try {
            const token = auth.token as string | null;
            if (!token) return false;
            const payload = JSON.parse(atob(token.split('.')[1]));
            return !!payload.is_superuser;
        } catch {
            return false;
        }
    })();

    // Check roles (compare against backend snake_case roles). Superuser bypasses.
    if (requiredRoles.length > 0) {
        const userRole = auth.user?.organizations?.[0]?.role;
        const hasRequiredRole = isSuperuser || (!!userRole && requiredRoles.includes(userRole));
        if (!hasRequiredRole) {
            throw redirect(302, '/unauthorized');
        }
    }

    // Check permissions. Superuser bypasses.
    if (requiredPermissions.length > 0) {
        if (!isSuperuser) {
            const userRole = auth.user?.organizations?.[0]?.role;
            const hasRequiredPermission = userRole === Role.TOOL_ADMIN;
            if (!hasRequiredPermission) {
                throw redirect(302, '/unauthorized');
            }
        }
    }

    return true;
}

// Predefined guard functions for common use cases
export const requireAuth = () => authGuard({ requireAuth: true });

export const requireAdmin = () => authGuard({
    requireAuth: true,
    requiredRoles: [Role.TOOL_ADMIN]
});

export const requireOrgAdmin = () => authGuard({
    requireAuth: true,
    requiredRoles: [Role.TOOL_ADMIN, Role.ORG_ADMIN]
});

export const requireRiskManager = () => authGuard({
    requireAuth: true,
    requiredRoles: [Role.TOOL_ADMIN, Role.ORG_ADMIN, Role.RISK_MANAGER]
});

export const requireAnalyst = () => authGuard({
    requireAuth: true,
    requiredRoles: [Role.TOOL_ADMIN, Role.ORG_ADMIN, Role.RISK_MANAGER, Role.TARA_ANALYST, Role.SECURITY_ENGINEER]
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
