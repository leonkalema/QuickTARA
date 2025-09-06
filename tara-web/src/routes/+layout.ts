import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';

export async function load({ url }) {
	// Only redirect on client side to avoid SSR issues
	if (browser) {
		const isAuthPage = url.pathname === '/auth';
		const isUnauthorizedPage = url.pathname === '/unauthorized';
		
		// Check if user is authenticated
		const token = localStorage.getItem('auth_token');
		const isAuthenticated = !!token;
		
		// Redirect unauthenticated users to auth page (except if already on auth or unauthorized page)
		if (!isAuthenticated && !isAuthPage && !isUnauthorizedPage) {
			throw redirect(302, '/auth');
		}
		
		// Redirect authenticated users away from auth page
		if (isAuthenticated && isAuthPage) {
			throw redirect(302, '/');
		}
	}
	
	return {};
}
